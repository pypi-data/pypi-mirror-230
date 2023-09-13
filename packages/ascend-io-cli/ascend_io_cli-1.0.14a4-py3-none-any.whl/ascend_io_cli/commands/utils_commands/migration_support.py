import base64
import re

import typer

from ascend_io_cli.support import _get_cli_options

GET_COMPONENT_STATE_METHODS = {
    'source': 'get_read_connector_state',
    'view': 'get_transform_state',
    'sink': 'get_write_connector_state',
}

GET_RECORD_STATISTICS_METHOD = {
    'source': 'get_read_connector_statistics',
    'view': 'get_transform_statistics',
    'sink': 'get_write_connector_statistics',
}


# Getting useful information for component, will add to single reason column
def is_legacy_component(ctx: typer.Context, client, component):
  yield from check_legacy_components(ctx, component)
  yield from check_custom_docker(ctx, client, component)
  yield from check_override_fingerprint(ctx, component)
  yield from check_FBA(ctx, client, component)
  yield from check_spark_override(ctx, component)
  yield from check_group_by_legacy_sql(ctx, component)
  yield from check_union_legacy_sql(ctx, component)
  yield from check_custom_python(ctx, component)


# Getting useful states for component, will add as a column
def get_state(ctx: typer.Context, client, component):
  paused = get_paused_state(ctx, client, component)
  status = get_error_state(ctx, client, component)
  partitions = get_partition_count_state(ctx, client, component) if status == "Up to Date" else -1
  records = get_record_count_state(ctx, client, component) if status == "Up to Date" else -1
  return {
      "paused": paused,
      "status": status,
      "partitions": partitions,
      "records": records,
  }

def check_custom_python(ctx: typer.Context, component) -> list:
  if component.type == "source":
    if "code_interface" in list(component.source.container.record_connection.details.keys()):
      yield "custom python RC"
  elif component.type == "view":
    if "python" in str(component.view.operator.spark_function.executable.code.language):
      yield "custom python transform"
  elif component.type == "sink":
    pass

def check_legacy_components(ctx: typer.Context, component) -> list:
  if component.type == "source":
    if not component.source.container.record_connection.connection_id.value:
      if component.source.container.s3.bucket:
        yield "legacy s3 RC"
      elif component.source.container.big_query.project:
        yield "legacy BQ RC"
      elif component.source.container.immediate.object:
        yield "legacy inline RC"
      elif component.source.container.gcs.bucket:
        yield "legacy gcs RC"
      elif component.source.container.abs.account_name:
        yield "legacy ADLS RC"
      elif component.source.container.byte_function.container.executable.code.source:
        yield "legacy custom RC"
      elif component.source.container.WhichOneof("details") != "record_connection":
        yield "uncaught legacy RC without connection"
  if component.type == "view":
    if component.view.operator.WhichOneof("details") == "sql_query":
      yield "legacy SQL query"
    if component.view.operator.spark_function.executable.code.language.java.class_name:
      yield "scala transform"
  if component.type == "sink":
    if not component.sink.container.record_connection.connection_id.value:
      yield "legacy WC"
    elif component.sink.container.WhichOneof("details") != "record_connection":
      yield "uncaught legacy sink without connection"


def check_custom_docker(ctx: typer.Context, client, component) -> list:
  if component.view.operator.spark_function.executable.code.environment.container_image.name:
    yield "custom docker component level"
  elif component.view.operator.spark_function.executable.code.environment.container_image_label:
    yield "custom docker component level"
  elif "parent_spark_environment" in str(component).lower():
    try:
      ds = client.get_data_service_runtime_environment(component.organization.id).data
      if ds.container_image.name:
        yield "custom docker dataservice level"
    except:
      pass


def check_override_fingerprint(ctx: typer.Context, component) -> list:
  if component.view.operator.spark_function.executable.code.source.override_fingerprint:
    yield "override fingerprint"
  elif "override_fingerprint" in str(component).lower():
    yield "override fingerprint (str match)"


def check_FBA(ctx: typer.Context, client, component) -> list:
  if component.source.container.record_connection.connection_id.value:
    # check FBA connection in connection
    connection_definition = client.get_connection(
        component.organization.id,
        component.source.container.record_connection.connection_id.value,
    ).data
    if "s3.ascend.io" in str(connection_definition).lower():
      yield "FBA in connection"
  if component.source.bytes.parser.lambda_parser.code.inline:
    # check FBA connection in component by proto path
    if b"s3.ascend.io" in base64.b64decode(component.source.bytes.parser.lambda_parser.code.inline).lower():
      yield "FBA in legacy python RC"
  if "s3.ascend.io" in str(component).lower():
    # check FBA connection in connection by string match
    yield "FBA in python"


def check_spark_override(ctx: typer.Context, component) -> list:
  if len(str(component.view.operator.spark_function.job_configuration)) > 0:
    yield "spark override"
  elif "job_configuration" in str(component).lower():
    # spark override for gen1 RC WC
    yield "spark override (str match 1)"
  elif "driver_instance_type" in str(component).lower():
    # spark override for gen2 RC WC
    yield "spark override (str match 2)"


def check_group_by_legacy_sql(ctx: typer.Context, component) -> list:
  if component.view.operator.WhichOneof("details") == "sql_query":
    if "group by " in component.view.operator.sql_query.sql.lower():
      yield "GROUP BY in legacy SQL"


def check_union_legacy_sql(ctx: typer.Context, component) -> list:
  if component.view.operator.WhichOneof("details") == "sql_query":
    pattern = re.compile(r"from (\s*[$]\{\d+\}\s*,?){2,}")
    match = pattern.search(component.view.operator.sql_query.sql.lower().replace("\n", ""))
    # print(component.view.operator.sql_query.sql.lower())
    if match:
      yield "UNION in legacy SQL"


def get_paused_state(ctx: typer.Context, client, component):
  if component.type == "source":
    return component.source.assigned_priority.paused
  elif component.type == "view":
    return component.view.assigned_priority.paused
  elif component.type == "sink":
    return component.sink.assigned_priority.paused


def get_error_state(ctx: typer.Context, client, component):
  method = getattr(client, GET_COMPONENT_STATE_METHODS[component.type])
  return method(component.organization.id, component.project.id, component.id) \
      .data \
      .state \
      .composite_state \
      .text


def get_partition_count_state(ctx: typer.Context, client, component):
  method = getattr(client, GET_RECORD_STATISTICS_METHOD[component.type])
  return method(component.organization.id, component.project.id, component.id) \
      .data \
      .statistics \
      .dimensions["__part_files__"] \
      .cardinality


def get_record_count_state(ctx: typer.Context, client, component):
  method = getattr(client, GET_RECORD_STATISTICS_METHOD[component.type])
  return method(component.organization.id, component.project.id, component.id) \
      .data \
      .statistics \
      .dimensions["__records__"] \
      .cardinality


def generate_component_url(ctx: typer.Context, component):
  hostname = _get_cli_options(ctx).hostname
  return f"https://{hostname}/ui/v2/organization/{component.organization.id}/project/{component.project.id}/{component.type}/{component.id}"
