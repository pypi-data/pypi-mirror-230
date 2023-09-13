from typing import Optional

import glog
import typer

from ascend_io_cli.commands.support.lineage_support import LineageSupport, OutputFormat
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


@app.command()
def lineage(ctx: typer.Context,
            data_service_id: str = typer.Argument(..., help='Data service id containing the flow and component to analyze'),
            dataflow_id: str = typer.Argument(..., help='Dataflow id containing the component to analyze'),
            component_id: str = typer.Argument(..., help='The component to use when describing the lineage flowing from end to end'),
            upstream: bool = typer.Option(False, help='Describe upstream lineage relative to the context component'),
            downstream: bool = typer.Option(False, help='Describe downstream lineage relative to the context component'),
            readers: bool = typer.Option(False, help='Describe readers for the lineage passing through the context component'),
            writers: bool = typer.Option(False, help='Describe writers for the lineage starting with the context component'),
            details: bool = typer.Option(False, help='Include component details such as schema and query information'),
            output: OutputFormat = typer.Option(None, help='Output the [bold green]entire[/bold green] graph in the specified format')):
  """Discover upstream, downstream, or all lineage relative to a supplied component id."""
  lineage_support = LineageSupport(get_client(ctx))
  lineage_graph = lineage_support.build_graph(data_service_id, dataflow_id, component_id, details=details)

  if output:
    str_out = output.generate(lineage_graph.graph)
    # override any contex specified in the command
    ctx.obj.output = 'objects'
    print_response(ctx, str_out)
  else:
    if readers:
      glog.debug('Process readers only')
      print_response(ctx, lineage_graph.readers())
    elif writers:
      glog.debug('Process writers only')
      print_response(ctx, lineage_graph.writers())
    elif not (upstream or downstream):
      glog.debug('Process lineage end-to-end')
      print_response(ctx, lineage_graph.end_to_end())
    elif upstream:
      glog.debug('Process lineage upstream only')
      print_response(ctx, lineage_graph.upstream())
    elif downstream:
      glog.debug('Process lineage downstream only')
      print_response(ctx, lineage_graph.downstream())
