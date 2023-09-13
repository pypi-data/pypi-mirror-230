import logging

import typer
from ascend.sdk.definitions import DataService

from ascend_io_cli.support import get_client, print_response

app = typer.Typer(name='create', help='Create a data service instance', no_args_is_help=True)


@app.command()
def data_service(
    ctx: typer.Context,
    data_service: str = typer.Argument(..., help='Data Service id', show_default=False),
    name: str = typer.Option(None, help='Data Service name if different than id'),
    description: str = typer.Option(None, help='Data Service description to use', show_default=False),
):
  """Create a Data Service"""
  client = get_client(ctx)
  logging.info(f"Creating data service '{data_service}' from host {ctx.obj.hostname}")
  ds = DataService(
      id=data_service,
      name=name if name else data_service,
      description=description,
  )
  response = client.create_data_service(body=ds.to_proto())
  print_response(ctx, response)
