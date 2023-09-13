#!/usr/bin/env python3
import datetime
from typing import List

import ascend.protos.api.api_pb2 as pb2
import ascend.protos.component.component_pb2 as component
import ascend.protos.function.function_pb2 as function
import ascend.protos.io.io_pb2 as io
import ascend.protos.operator.operator_pb2 as operator
import typer
from ascend.sdk import definitions

from ascend_io_cli.support import get_client, print_response, type_factory

app = typer.Typer(help='Build basic dataflow components', no_args_is_help=True)

NL = '\n,'

GET_SCHEMA_METHODS = {
    'source': 'get_read_connector_schema',
    'view': 'get_transform_schema',
}


def _fields(schema: str):
  return [f.split(' ')[0] for f in schema.split(',')]


def _language_factory(data_service_type: str) -> function.Code.Language:
  if data_service_type == "snowflake":
    return function.Code.Language(snowflake_sql=function.Code.Language.SnowflakeSql(), )
  elif data_service_type == "databricks":
    return function.Code.Language(databricks_sql=function.Code.Language.DatabricksSql(), )
  elif data_service_type == "motherduck":
    return function.Code.Language(motherduck_sql=function.Code.Language.MotherDuckSql(), )
  elif data_service_type == "bigquery":
    return function.Code.Language(bigquery_sql=function.Code.Language.BigQuerySql(), )

  raise ValueError(f"'Data Service type '{data_service_type}' is not supported.'")


def _build_transform(data_service_type: str, input_component: pb2.Transform, input_schema: pb2.ComponentSchemaResponse.Schema, join_columns: List[str]):
  fields = _fields(input_schema.schema)
  merge_transform = definitions.Transform(
      id=f'{input_component.id}_Merge_Transform',
      name=f'{input_component.name} Merge Transform',
      description=f"Merge from component '{input_component.name}' ({input_component.id}) created with CLI at {datetime.datetime.now()}",
      input_ids=[
          input_component.id,
      ],
      operator=operator.Operator(spark_function=operator.Spark.Function(
          executable=io.Executable(code=io.Code(
              language=_language_factory(data_service_type),
              source=io.Code.Source(inline=f"""MERGE INTO {{{{target}}}} as t USING (
  SELECT 
    *
  FROM
    {{{{{input_component.id}}}}}
  ) as s 
    ON {' AND '.join(['t.{0} = s.{0}'.format(col) for col in join_columns])}
  WHEN MATCHED THEN
    UPDATE
    SET {','.join(['t.{0} = s.{0}'.format(col) for col in fields])}
  WHEN NOT MATCHED THEN
    INSERT
      ({','.join(fields)})
    VALUES
      ({','.join(['s.{0}'.format(col) for col in fields])})
  """, ),
              additional_source=io.Code.Source(
                  inline=f"CREATE TABLE IF NOT EXISTS {{{{target}}}} ({NL.join(type_factory(data_service_type, input_schema.schema.split(',')))})"),
          ), ),
          reduction=operator.Reduction(full=operator.Reduction.Full(), ),
          tests=function.QualityTests(),
      ), ),
      assigned_priority=component.Priority(),
  )
  id_map = {input_component.id: definitions.ComponentUuidType(type=input_component.type, uuid=input_component.uuid)}
  return merge_transform, id_map


@app.command()
def merge(
    ctx: typer.Context,
    data_service_id: str = typer.Argument(..., help='Data Service id', show_default=False),
    dataflow_id: str = typer.Argument(..., help='Dataflow id', show_default=False),
    component_id: str = typer.Argument(..., help='Transformation component id to merge from', show_default=False),
    join_columns: List[str] = typer.Argument(..., help='Columns that join source to target', show_default=False),
):
  """Build a basic merge component from an existing transformation that you can use as a template to get started."""
  client = get_client(ctx)

  data_service = client.get_data_service(data_service_id).data
  components = client.list_dataflow_components(data_service_id, dataflow_id, kind='source,view').data

  upstream_component = [c for c in components if c.id == component_id]

  if not upstream_component:
    raise Exception(f'Component {data_service_id}.{dataflow_id}.{component_id} not found. Is the merge source component a read or transform component?')

  # get the schema information in the string (easier)
  schema_method = getattr(client, GET_SCHEMA_METHODS[upstream_component[0].type])
  upstream_schema = schema_method(data_service_id, dataflow_id, component_id).data
  if not upstream_schema:
    raise Exception(f'Schema for component {data_service_id}.{dataflow_id}.{component_id} not found.')

  # build the transformation
  merge_transform, id_map = _build_transform(data_service.data_service_type, upstream_component[0], upstream_schema, join_columns)

  # actually send the transform
  resp = client.create_transform(data_service_id, dataflow_id, merge_transform.to_proto(id_map))
  print_response(ctx, resp.data)


if __name__ == "__main__":
  app()
