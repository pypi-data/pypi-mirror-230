import concurrent
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import typer

from ascend_io_cli.support import COMPONENT_METHODS, re_matcher, not_blank, get_client, print_response

app = typer.Typer(help='Reset component errors', no_args_is_help=True)


class ResetErrorException(Exception):
  def __init__(self, service, flow, component, exception: Exception):
    self._service = service
    self._flow = flow
    self._component = component
    self._exception = exception

  def __str__(self):
    return f'{self._service}.{self._flow}.{self._component} -> {self._exception}'


@app.callback(invoke_without_command=True)
def reset_errors(
    ctx: typer.Context,
    service_matching: str = typer.Option(
        None,
        '--data-services',
        help='Reset components in data services by matching service name',
        show_default=False,
    ),
    flows_matching: str = typer.Option(
        None,
        '--dataflows',
        help='Reset components in dataflows by matching flow name',
        show_default=False,
    ),
    component_matching: str = typer.Option(
        None,
        '--components',
        help='Reset components by matching component name',
        show_default=False,
    ),
    error_matching: str = typer.Option(
        None,
        '--error',
        help='Reset components with matching error text (regex)',
        show_default=False,
    ),
    regex: Optional[bool] = typer.Option(False, help='Match names using regex expressions'),
):
  client = get_client(ctx)

  service_re = re_matcher(service_matching, regex)
  flow_re = re_matcher(flows_matching, regex)
  component_re = re_matcher(component_matching, regex)
  error_re = re_matcher(error_matching, False)

  def reset_component_errors(service, flow, component):
    call_reset = False
    if component and component.type and COMPONENT_METHODS.get(component.type, None):
      comp_type = COMPONENT_METHODS[component.type]
      error_method = getattr(client, f'get_{comp_type}_errors')
      error_resp = error_method(service.id, flow.id, component.id, offset=0, limit=1).data
      if error_resp.errors and len(error_resp.errors.error):
        if error_re:
          for err in error_resp.errors.error:
            if err.fault and not_blank(err.fault.description) and error_re.match(err.fault.description):
              call_reset = True
              break
        else:
          call_reset = True
        if call_reset:
          logging.debug(f'resetting errors for {service.id}.{flow.id}.{component.id}[{comp_type}]')
          try:
            reset_method = getattr(client, f'reset_{comp_type}_errors')
            reset_method(service.id, flow.id, component.id, 1)
          except Exception as ex:
            raise ResetErrorException(service, flow, component, ex)
    return {
        'data-service': service.name,
        'data-service-id': service.id,
        'dataflow': flow.name,
        'dataflow-id': flow.id,
        'component': component.name,
        'component-id': component.id,
        'reset': call_reset
    }

  futures = []
  results = []
  with ThreadPoolExecutor(max_workers=ctx.obj.workers) as executor:
    for ds in client.list_data_services().data:
      if not service_re or service_re.match(ds.name):
        for df in client.list_dataflows(data_service_id=ds.id).data:
          if not flow_re or flow_re.match(df.name):
            for comp in client.list_dataflow_components(data_service_id=ds.id, dataflow_id=df.id).data:
              if not component_re or component_re.match(comp.name):
                futures.append(executor.submit(reset_component_errors, ds, df, comp))
    for future in concurrent.futures.as_completed(futures):
      try:
        result = future.result(10)
        if result.get('reset', False):
          results.append(result)
      except ResetErrorException as e:
        logging.info(e)
  print_response(ctx, results)
