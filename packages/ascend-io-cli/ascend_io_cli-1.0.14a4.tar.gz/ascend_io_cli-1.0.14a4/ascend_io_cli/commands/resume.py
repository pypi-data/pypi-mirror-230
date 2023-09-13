from typing import List, Optional

import typer

from ascend_io_cli.commands.pause import pause_resume_components

app = typer.Typer(help='Resume component execution optionally filtered by state', no_args_is_help=True)


@app.command()
def component(
    ctx: typer.Context,
    data_service_id: str = typer.Argument(..., help='Data Service id', show_default=False),
    dataflow_id: str = typer.Argument(..., help='Dataflow id', show_default=False),
    component_id: List[str] = typer.Argument(..., help='List of component ids to resume', show_default=False),
    state: Optional[List[str]] = typer.Option([], help='List of states of components to resume (uptodate, running, outofdate, error)'),
):
  """Resume a list of components"""
  pause_resume_components(ctx, False, data_service_id, dataflow_id, component_id, state)


@app.command()
def dataflow(
    ctx: typer.Context,
    data_service_id: str = typer.Argument(..., help='Data Service id', show_default=False),
    dataflow_id: str = typer.Argument(..., help='Dataflow id', show_default=False),
    state: Optional[List[str]] = typer.Option([], help='List of states of components to resume (uptodate, running, outofdate, error)'),
):
  """Resume all components in a dataflow"""
  pause_resume_components(ctx, False, data_service_id, dataflow_id, [], state)
