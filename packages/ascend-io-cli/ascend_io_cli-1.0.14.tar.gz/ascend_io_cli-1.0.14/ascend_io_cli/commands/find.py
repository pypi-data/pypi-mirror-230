from typing import Optional

import typer

from ascend_io_cli.support import get_client, print_response, re_matcher

app = typer.Typer(help='Find data-services, dataflows, and components', no_args_is_help=True)


@app.command()
def components(
    ctx: typer.Context,
    field_name: str = typer.Argument(..., help='Find components with schema fields containing this text and ignoring case'),
    data_service: str = typer.Option(
        None,
        '--data-service',
        help='Name of specific data-service to look in',
    ),
    dataflow: str = typer.Option(
        None,
        '--dataflow',
        help='Name of specific dataflow to look in',
    ),
    regex: Optional[bool] = typer.Option(False, help='Match names using regex expressions'),
):
  if not field_name:
    return []

  def match_fields(comp, find_reg):
    fields = []
    if comp.schema:
      for field in comp.schema.map.field:
        fields.append(field)
    if comp.view:
      for field in comp.view.status.schema.map.field:
        fields.append(field)
    if comp.source:
      for field in comp.source.status.schema.map.field:
        fields.append(field)
    for field in fields:
      if find_reg.match(field.name):
        return comp

  client = get_client(ctx)
  data = []
  find_re = re_matcher(field_name, regex)
  for ds in client.list_data_services().data:
    if not data_service or ds.name == data_service:
      for df in client.list_dataflows(ds.name).data:
        if not dataflow or df.name == dataflow:
          for df_component in client.list_dataflow_components(ds.name, df.name, deep=True, kind='source,view,pub,sub').data:
            match_component = match_fields(df_component, find_re)
            if match_component:
              data.append(match_component)
  print_response(ctx, data)
