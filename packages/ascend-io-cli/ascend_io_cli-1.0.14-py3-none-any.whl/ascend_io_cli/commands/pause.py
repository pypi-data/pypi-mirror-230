import concurrent
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import glog
import typer
from google.protobuf.json_format import MessageToDict
import ascend.protos.api.api_pb2 as api_pb2

from ascend_io_cli.support import get_client, print_response, COMPONENT_PAUSE_METHODS

app = typer.Typer(help='Pause component execution optionally filtered by state', no_args_is_help=True)


@app.command()
def component(
    ctx: typer.Context,
    data_service_id: str = typer.Argument(..., help='Data Service id containing the component to pause', show_default=False),
    dataflow_id: str = typer.Argument(..., help='Dataflow id containing the component to pause', show_default=False),
    component_id: List[str] = typer.Argument(..., help='List of component ids to pause', show_default=False),
    state: Optional[List[str]] = typer.Option([], help='List of states of components to pause (uptodate, running, outofdate, error)'),
):
  """Pause a list of components"""
  pause_resume_components(ctx, True, data_service_id, dataflow_id, component_id, state)


@app.command()
def dataflow(
    ctx: typer.Context,
    data_service_id: str = typer.Argument(..., help='Data Service id containing dataflow to pause', show_default=False),
    dataflow_id: str = typer.Argument(..., help='Dataflow id to pause all components', show_default=False),
    state: Optional[List[str]] = typer.Option([], help='List of states of components to pause (uptodate, running, outofdate, error)'),
):
  """Pause all components in a dataflow"""
  pause_resume_components(ctx, True, data_service_id, dataflow_id, [], state)


def pause_resume_components(ctx: typer.Context, pause_flag: bool, service_id: str, flow_id: str, component_id: List[str], state: List[str]):
  client = get_client(ctx)

  def _pause_resume(target_component: api_pb2.Component, pause: bool):
    if COMPONENT_PAUSE_METHODS.get(target_component.type, None):
      glog.debug(f'{"Pausing" if pause else "Resuming"} component {target_component.id}')
      return getattr(client, COMPONENT_PAUSE_METHODS[target_component.type])(data_service_id=target_component.organization.id,
                                                                             dataflow_id=target_component.project.id,
                                                                             id=target_component.id,
                                                                             body='{}',
                                                                             paused=pause).data
    return None

  results = []
  if service_id and flow_id:
    components = client.list_dataflow_components(service_id, flow_id, deep=False, kind='source,view,sink', state=','.join(state)).data

    glog.debug(f"_pause_resume {service_id}.{flow_id} with {ctx.obj.workers} worker threads")
    with ThreadPoolExecutor(max_workers=int(ctx.obj.workers)) as executor:
      futures = [executor.submit(_pause_resume, c, pause_flag) for c in components if not component_id or (c.id in component_id)]

      for future in concurrent.futures.as_completed(futures, timeout=29.0):
        result = future.result(11.0)
        results.append(MessageToDict(result))

  print_response(ctx, results)
