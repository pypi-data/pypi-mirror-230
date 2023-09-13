import logging
from typing import Optional

import typer

from ascend_io_cli.support import get_client, print_response
from .migration_support import generate_component_url, get_state, is_legacy_component

app = typer.Typer(help='Gen1 -> Gen2 migration.', no_args_is_help=True)


@app.command()
def legacy_components(
    ctx: typer.Context,
    data_service: Optional[str] = typer.Option(None, help='Data Service id - required if using a dataflow id'),
    dataflow: Optional[str] = typer.Option(None, help='Dataflow id'),
):
  if dataflow and not data_service:
    typer.echo('Service is required if using a flow id')
    raise typer.Exit(code=1)

  client = get_client(ctx)
  if data_service and not dataflow:
    components = client.list_data_service_components(data_service_id=data_service, deep=True).data
  elif dataflow:
    components = client.list_dataflow_components(data_service_id=data_service, dataflow_id=dataflow, deep=True).data
  else:
    components = [c for ds in client.list_data_services().data for c in client.list_data_service_components(data_service_id=ds.id, deep=True).data]

  data = []
  for component in components:
    reason = list(is_legacy_component(ctx, client, component))
    if reason:
      try:
        states = get_state(ctx, client, component)
      except Exception as e:
        logging.debug(f'Failed to get state for {component.id}: {e}')
        states = {}
      data.append({
          'data_service_id': component.organization.id,
          'dataflow_id': component.project.id,
          'component_id': component.id,
          'component_type': component.type,
          'reason': reason,
          **states, 
          'url': generate_component_url(ctx, component)
      })
  print_response(ctx, data)
