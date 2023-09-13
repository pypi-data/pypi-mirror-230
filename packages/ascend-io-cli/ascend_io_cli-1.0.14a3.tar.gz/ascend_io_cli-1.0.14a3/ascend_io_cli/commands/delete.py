import logging
from typing import Optional

import typer

from ascend_io_cli.support import get_client, print_response, COMPONENT_DELETE_METHODS

app = typer.Typer(name='delete', help='Delete data services and dataflows', no_args_is_help=True)


@app.command()
def data_service(
    ctx: typer.Context,
    data_service: Optional[str] = typer.Argument(..., help='Data Service id', show_default=False),
):
  """Delete a data service. Cannot be undone."""
  client = get_client(ctx)
  logging.info(f"Deleting data service '{data_service}' from host {ctx.obj.hostname}")
  obj = client.get_data_service(data_service_id=data_service).data
  client.delete_data_service(data_service_id=data_service)
  print_response(ctx, obj)


@app.command()
def dataflow(
    ctx: typer.Context,
    data_service: Optional[str] = typer.Argument(..., help='Data Service id', show_default=False),
    dataflow: Optional[str] = typer.Argument(..., help='Dataflow id', show_default=False),
):
  """Delete a dataflow from a service. Cannot be undone."""
  client = get_client(ctx)
  logging.debug(f"Deleting dataflow '{data_service}.{dataflow}' from host {ctx.obj.hostname}")
  obj = client.get_dataflow(data_service_id=data_service, dataflow_id=dataflow).data
  client.delete_dataflow(data_service_id=data_service, dataflow_id=dataflow)
  print_response(ctx, obj)


@app.command()
def component(
    ctx: typer.Context,
    data_service: Optional[str] = typer.Argument(..., help='Data Service id', show_default=False),
    dataflow: Optional[str] = typer.Argument(..., help='Dataflow id', show_default=False),
    component: Optional[str] = typer.Argument(..., help='Component id', show_default=False),
):
  """Delete a component from a flow. Cannot be undone."""
  client = get_client(ctx)

  components = [c for c in client.list_dataflow_components(data_service_id=data_service, dataflow_id=dataflow).data if c.id == component]

  for c in components:
    if c.type in COMPONENT_DELETE_METHODS:
      delete_method = getattr(client, COMPONENT_DELETE_METHODS.get(c.type, None))
      delete_method(data_service_id=data_service, dataflow_id=dataflow, id=c.id)
  print_response(ctx, components)
