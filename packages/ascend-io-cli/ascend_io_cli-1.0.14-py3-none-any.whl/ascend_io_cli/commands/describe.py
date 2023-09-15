from typing import Optional

import typer
from ascend_io_cli.support import get_client, print_response

app = typer.Typer(help='Get data service, dataflow, and component details', no_args_is_help=True)


@app.command()
def component(
    ctx: typer.Context,
    data_service: Optional[str] = typer.Argument(..., help='Data Service id'),
    dataflow: Optional[str] = typer.Argument(..., help='Dataflow id'),
    component: Optional[str] = typer.Argument(..., help='Component id'),
):
  """Get component details"""
  client = get_client(ctx)
  data = [c for c in client.list_dataflow_components(data_service_id=data_service, dataflow_id=dataflow, deep=True).data if c.id == component]

  print_response(ctx, data[0])


@app.command()
def dataflow(
    ctx: typer.Context,
    data_service: Optional[str] = typer.Argument(..., help='Data Service id'),
    dataflow: Optional[str] = typer.Argument(..., help='Dataflow id'),
):
  """Get dataflow details"""
  client = get_client(ctx)
  data = [f for f in client.list_dataflows(data_service_id=data_service).data if f.id == dataflow]

  print_response(ctx, data[0])


@app.command()
def data_service(
    ctx: typer.Context,
    data_service: Optional[str] = typer.Argument(..., help='Data Service id'),
):
  """Get data service details"""
  client = get_client(ctx)
  data = [ds for ds in client.list_data_services().data if ds.id == data_service]

  print_response(ctx, data[0])
