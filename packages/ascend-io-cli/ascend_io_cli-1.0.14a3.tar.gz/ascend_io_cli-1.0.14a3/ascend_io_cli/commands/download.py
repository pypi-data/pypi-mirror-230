import concurrent
import fnmatch
import logging
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List

import typer
from ascend.sdk.render import TEMPLATES_V2, download_component, download_data_service, download_dataflow
from google.protobuf.json_format import MessageToDict

from ascend_io_cli.support import get_client, print_response

app = typer.Typer(help='Download local images of data services, dataflows, and components', no_args_is_help=True)


def _configure_write_dir(write_dir: Path, unique: bool) -> Path:
  write_dir = write_dir.resolve().joinpath(f'{datetime.now().strftime("%Y%m%d%H%M%S") if unique else ""}')
  if not os.path.exists(write_dir):
    os.makedirs(write_dir, exist_ok=True)
  return write_dir


def _load_ignore_matches(write_dir: Path) -> List[str]:
  ignore = []
  ignore_file = write_dir.joinpath('.ascendignore')
  if ignore_file.exists():
    with ignore_file.open('r', encoding='UTF-8') as file:
      while line := file.readline():
        line = line.strip()
        if line:
          ignore.append(line)
  if '.git' not in ignore:
    ignore.append('.git')
  if '.ascendignore' not in ignore:
    ignore.append('.ascendignore')
  return ignore


def _files_accepted(matches: List[str], base_dir: Path) -> List[str]:
  """Identify the files that should be accepted for cleanup.
  Ignores files that should be kept/preserved."""
  accepted_files = []

  for root, dirnames, filenames in os.walk(base_dir, topdown=True):
    for dirname in dirnames:
      for ignore in matches:
        if fnmatch.fnmatch(dirname, ignore) or fnmatch.fnmatch(dirname + '/', ignore):
          dirnames.remove(dirname) # remove any ignored directories from further consideration in os.walk

    for filename in filenames:
      full_file_path = os.path.join(root, filename)
      keep_file = True
      for ignore in matches:
        if fnmatch.fnmatch(full_file_path, ignore) or fnmatch.fnmatch(filename, ignore) or filename == ignore:
          keep_file = False
          break
      if keep_file:
        accepted_files.append(full_file_path)

  return accepted_files


def _clean_write_dir(write_dir: Path, purge: bool):
  """The purge option will remove everything"""
  if write_dir and write_dir.exists():
    assert write_dir != '/' # never remove root protection

    if purge:
      shutil.rmtree(write_dir)
    else:
      # assume .ascendignore in current working directory
      ignore_files = _load_ignore_matches(Path('.'))
      files = _files_accepted(ignore_files, write_dir)
      files.reverse()
      for f in files:
        os.remove(f)


@app.command()
def data_service(
    ctx: typer.Context,
    data_service: str = typer.Argument(None, help='Data Service id to download', show_default=False),
    base_dir: str = typer.Option('./ascend', help='Base directory to write the service and flows'),
    omit_data_service_dir: bool = typer.Option(False, help='Omit the data-service folder from the directory structure if downloading a single data service'),
    purge: bool = typer.Option(False, help='Include deleting .git and other data'),
    unique: bool = typer.Option(False, help='Create unique base directory'),
    template_dir: str = typer.Option(TEMPLATES_V2, '--template_dir', show_default=False),
):
  """Download service or all services (default). The default layout will be '<base-dir>/<data-service-name>' """
  client = get_client(ctx)

  omit_data_service_dir = False if data_service is None else omit_data_service_dir

  def _download_service(ds):
    calc_base_dir = Path(base_dir).resolve()
    calc_base_dir = calc_base_dir if omit_data_service_dir else calc_base_dir.joinpath(ds.id)
    calc_base_dir = _configure_write_dir(calc_base_dir, unique)
    _clean_write_dir(calc_base_dir, purge)
    download_data_service(client=client, data_service_id=ds.id, resource_base_path=str(calc_base_dir), template_dir=template_dir)
    return ds

  futures = []
  with ThreadPoolExecutor(max_workers=ctx.obj.workers) as executor:
    for svc in client.list_data_services().data:
      if not data_service or (data_service and data_service == svc.id):
        futures.append(executor.submit(_download_service, svc))

  results = []
  for future in concurrent.futures.as_completed(futures):
    result = future.result(10)
    logging.debug(f'downloaded {result.id}')
    results.append(MessageToDict(result))
  print_response(ctx, results)


@app.command()
def dataflow(
    ctx: typer.Context,
    data_service: str = typer.Argument(..., help='Data Service id containing dataflow to download', show_default=False),
    dataflow: str = typer.Argument(..., help='Dataflow id to download', show_default=False),
    base_dir: str = typer.Option('./ascend', help='Base directory to write the data service and flow'),
    omit_data_service_dir: bool = typer.Option(False, help='Omit the data-service folder from the directory structure'),
    omit_dataflow_dir: bool = typer.Option(False, help='Omit the dataflow folder from the directory structure'),
    purge: bool = typer.Option(False, help='Include deleting .git and other data'),
    unique: bool = typer.Option(False, help='Create unique base directory'),
    template_dir: str = typer.Option(TEMPLATES_V2, '--template_dir', show_default=False),
):
  """Download a dataflow into a local directory. The default layout will be '<base-dir>/<data-service-name>/<dataflow-name>' """
  client = get_client(ctx)

  flow_obj = client.get_dataflow(data_service_id=data_service, dataflow_id=dataflow).data
  if flow_obj:
    resource_base_path = Path(base_dir).resolve()
    if not omit_data_service_dir:
      resource_base_path = resource_base_path.joinpath(data_service)
    if not omit_dataflow_dir:
      resource_base_path = resource_base_path.joinpath(dataflow)

    resource_base_path = _configure_write_dir(resource_base_path, unique)
    _clean_write_dir(resource_base_path, purge)

    download_dataflow(client, data_service_id=data_service, dataflow_id=flow_obj.id, resource_base_path=str(resource_base_path), template_dir=template_dir)

  print_response(ctx, MessageToDict(flow_obj))


@app.command()
def component(
    ctx: typer.Context,
    data_service: str = typer.Argument(..., help='Data Service id with component to download', show_default=False),
    dataflow: str = typer.Argument(..., help='Dataflow id with component to download', show_default=False),
    component: str = typer.Argument(..., help='Component id to download', show_default=False),
    base_dir: str = typer.Option('./ascend', help='Base directory to write to'),
    omit_data_service_dir: bool = typer.Option(False, help='Omit the data-service folder from the directory structure'),
    omit_dataflow_dir: bool = typer.Option(False, help='Omit the dataflow folder from the directory structure'),
    omit_component_dir: bool = typer.Option(False, help='Omit the component folder from the directory structure'),
    purge: bool = typer.Option(False, help='Include deleting .git and other data'),
    unique: bool = typer.Option(False, help='Create unique base directory'),
    template_dir: str = typer.Option(TEMPLATES_V2, '--template_dir', show_default=False),
):
  """Download an individual component into a local directory. The default layout will be '<base-dir>/<data-service-name>/<dataflow-name>/components' """
  client = get_client(ctx)

  components = client.list_dataflow_components(data_service_id=data_service, dataflow_id=dataflow).data
  target_component = list(filter(lambda c: c.id == component, components))
  resource_base_path = Path(base_dir).resolve()
  if not omit_data_service_dir:
    resource_base_path = resource_base_path.joinpath(data_service)
  if not omit_dataflow_dir:
    resource_base_path = resource_base_path.joinpath(dataflow)
  if not omit_component_dir:
    resource_base_path = resource_base_path.joinpath('components')
  resource_base_path = _configure_write_dir(resource_base_path, unique)
  _clean_write_dir(resource_base_path, purge)

  download_component(client,
                     data_service_id=data_service,
                     dataflow_id=dataflow,
                     component_id=component,
                     resource_base_path=str(resource_base_path),
                     template_dir=template_dir)

  print_response(ctx, MessageToDict(target_component[0] if len(target_component) else {}))
