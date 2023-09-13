import json
import logging
import logging.config
import os
import re
from enum import Enum
from pathlib import Path
from typing import Any, Iterable

import glog
import typer
import yaml
from ascend.sdk.client import Client

og_print = print
from rich import print
from rich.table import Table

COMPONENT_METHODS = {
    'source': 'read_connector',
    'view': 'transform',
    'sink': 'write_connector',
}

COMPONENT_PAUSE_METHODS = {
    'source': 'update_read_connector_paused_state',
    'view': 'update_transform_paused_state',
    'sink': 'update_write_connector_paused_state',
}

COMPONENT_PARTITIONS_METHODS = {
    'source': 'get_read_connector_partitions',
    'view': 'get_transform_partitions',
    'sink': 'get_write_connector_partitions',
}

COMPONENT_DELETE_METHODS = {
    'source': 'delete_read_connector',
    'view': 'delete_transform',
    'sink': 'delete_write_connector',
    'group': 'delete_component_group',
    'pub': 'delete_data_feed',
    'sub': 'delete_data_feed_connector',
}

DEFAULT_WORKERS: int = 3


class CliOptions:
  def __init__(
      self,
      hostname: str = None,
      indent: int = None,
      output: str = None,
      workers: int = None,
      verify_ssl: bool = True,
      access_token: str = None,
  ):
    self.indent = indent
    self.hostname = hostname
    self.output = output
    self.workers = workers
    self.verify_ssl = verify_ssl
    self.access_token = access_token


def re_matcher(s: str, is_regex: bool):
  # if the expression is not a regex, treat it like a 'string contains' regular expression
  return re.compile(s if is_regex else ".*" + re.escape(s) + ".*", re.IGNORECASE) if not_blank(s) else None


def not_blank(s):
  return bool(s and isinstance(s, str) and s.strip())


def _get_cli_options(ctx: typer.Context) -> CliOptions:
  if not ctx.obj:
    ctx.obj = CliOptions()
  return ctx.obj


class JSONDefinitionEncoder(json.JSONEncoder):
  def default(self, obj):
    import google.protobuf.json_format as json_format
    import google.protobuf.message as message
    if issubclass(type(obj), message.Message):
      return json_format.MessageToDict(obj)
    return vars(obj)


def print_response(ctx: typer.Context, data):
  import ascend.sdk.definitions as definitions
  import google.protobuf.message as message
  _get_cli_options(ctx)

  output = ctx.obj.output

  if output == 'objects':
    print(data)

  elif output == 'table':
    if issubclass(type(data), list) and len(data) > 0 and hasattr(data[0], 'keys'):
      keys = sorted(list(set().union(*[list(o.keys()) for o in data])))
      table = Table(*keys, show_lines=False, show_edge=False)
      for o in data:
        table.add_row(*[str(o.get(k, '')) for k in keys])
      print(table)
    else:
      for o in data:
        if type(o) != str:
          o = json.dumps(o)
        og_print(o)

  elif output in ['json', 'yaml']:
    type_check = data
    if issubclass(type(data), list) and len(data) > 0:
      type_check = data[0]

    cls = None
    if issubclass(type(type_check), definitions.Definition) or issubclass(type(type_check), message.Message) or ():
      cls = JSONDefinitionEncoder

    json_str = json.dumps(data, indent=int(ctx.obj.indent) if ctx.obj.indent else 2, cls=cls)
    if output == 'json':
      print(json_str)
    else:
      print(yaml.dump(json.loads(json_str)))

  else:
    raise Exception(f'Unknown output format: {output}')


def _defaults_file_name():
  path = Path.home().joinpath('.ascend', 'cli-default.yml')
  if not os.path.exists(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w'):
      pass
  return path


def _load_default_map(ctx: typer.Context):
  if ctx and not ctx.default_map:
    config_file = _defaults_file_name()
    logging.debug(f'Loading config file: {str(config_file)}')
    try:
      with open(config_file, 'r') as f:
        conf = yaml.safe_load(f)
      ctx.default_map = ctx.default_map or {}
      if conf:
        ctx.default_map.update(conf)
    except Exception as ex:
      raise typer.BadParameter(str(ex))
  return ctx.default_map if ctx else {}


class OutputFormat(str, Enum):
  json = "json"
  objects = "objects"
  table = "table"
  yaml = "yaml"


def output_callback(ctx: typer.Context, value: OutputFormat):
  _load_default_map(ctx)
  _get_cli_options(ctx).output = value.name if value else ctx.default_map.get('output', OutputFormat.json)
  return value


def max_workers_callback(ctx: typer.Context, value: int):
  _load_default_map(ctx)
  _get_cli_options(ctx).workers = (ctx.default_map.get('workers', DEFAULT_WORKERS) if value else None)
  return value


def verbosity_callback(ctx: typer.Context, verbosity: str):
  _load_default_map(ctx)
  if verbosity:
    verbosity = verbosity.upper()
    logger = logging.getLogger()
    logger.setLevel(verbosity)
    glog.setLevel(verbosity)
    logger.info(f'Logging verbosity changed to {verbosity}')
  return verbosity


def verify_ssl_callback(ctx: typer.Context, value: bool):
  _get_cli_options(ctx).verify_ssl = value


def access_token_callback(ctx: typer.Context, value: str):
  _get_cli_options(ctx).access_token = value


def param_callback(
    ctx: typer.Context,
    param,
    value: any,
):
  _load_default_map(ctx)
  return value if value else ctx.default_map.get(param.name, None)


def hostname_callback(
    ctx: typer.Context,
    param,
    value: any,
):
  _load_default_map(ctx)
  final_value = value if value else ctx.default_map.get(param.name, None)
  opts = _get_cli_options(ctx)
  opts.hostname = final_value
  logging.debug(f'Using SDK host: {final_value}')
  return final_value


def get_client(ctx: typer.Context):
  verify_ssl = _get_cli_options(ctx).verify_ssl
  access_token = _get_cli_options(ctx).access_token
  logging.debug(f'SSL Verification: {verify_ssl}')
  if not verify_ssl:
    logging.warning('SSL Verification Disabled!')
  return Client(hostname=_get_cli_options(ctx).hostname, verify_ssl=verify_ssl, access_token=access_token)


def type_factory(data_service_type: str, schema: Any) -> Any:
  """We are writing raw SQL so replace types that won't directly translate"""
  if data_service_type == "snowflake":
    return to_snowflake_types(schema)
  elif data_service_type == "databricks":
    return schema
  elif data_service_type == "motherduck":
    return schema
  elif data_service_type == "bigquery":
    return to_bigquery_types(schema)

  raise ValueError(f"'Data Service type '{data_service_type}' is not supported.'")


SNOWFLAKE_TYPE_RE = [
    (re.compile('(\s+)long', re.IGNORECASE), r'\1NUMERIC(38,0)'),
]


def to_snowflake_types(schema: Any) -> Any:
  if isinstance(schema, str):
    for r in SNOWFLAKE_TYPE_RE:
      schema = r[0].sub(r[1], schema)
  elif issubclass(type(schema), Iterable):
    for i, t in enumerate(schema):
      for r in SNOWFLAKE_TYPE_RE:
        t = r[0].sub(r[1], t)
      schema[i] = t

  return schema


BIGQUERY_TYPE_RE = [
    (re.compile('(\s+)ARRAY', re.IGNORECASE), r'\1ARRAY<STRING>'),
    (re.compile('(\s+)long', re.IGNORECASE), r'\1INTEGER'),
    (re.compile('NUMERIC\((29|30|31|32|33|34|35|36|37|38)\)', re.IGNORECASE), r'NUMERIC(28)'),
    (re.compile('NUMERIC\((29|30|31|32|33|34|35|36|37|38)\s*,\s*([0-9]+)\)', re.IGNORECASE), r'NUMERIC(28,\2)'),
]


def to_bigquery_types(schema: Any) -> Any:
  if isinstance(schema, str):
    for r in BIGQUERY_TYPE_RE:
      schema = r[0].sub(r[1], schema)
  elif issubclass(type(schema), Iterable):
    for i, t in enumerate(schema):
      for r in BIGQUERY_TYPE_RE:
        t = r[0].sub(r[1], t)
      schema[i] = t

  return schema
