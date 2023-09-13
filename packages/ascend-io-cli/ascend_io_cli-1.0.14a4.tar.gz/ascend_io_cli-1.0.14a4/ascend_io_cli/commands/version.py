import importlib.metadata

import glog as log
import typer
from google.protobuf.json_format import MessageToDict

from ascend_io_cli import __version__
from ascend_io_cli.support import print_response, get_client

app = typer.Typer(help='Show the CLI version')


@app.callback(invoke_without_command=True)
def version(
    ctx: typer.Context,
    local_only: bool = typer.Option(False, help='Only show local version', show_default=False),
):
  """Retrieve version information for the CLI, SDK, and the currently targeted Ascend host."""
  # local version
  ver = {
      'cli-version': __version__,
      'sdk-version': importlib.metadata.version('ascend-io-sdk'),
      'hostname': ctx.obj.hostname,
  }

  if not local_only:
    # remote versions
    log.debug('getting server version')
    client = get_client(ctx)
    remote_version = client.get_ascend_version()
    if remote_version.response_code == 200 and remote_version.data:
      log.debug(f'remote server versions: {remote_version.data}')
      ver_dict = MessageToDict(remote_version.data)
      for k in ver_dict:
        ver[k] = ver_dict[k]

  print_response(ctx, ver)
  raise typer.Exit()
