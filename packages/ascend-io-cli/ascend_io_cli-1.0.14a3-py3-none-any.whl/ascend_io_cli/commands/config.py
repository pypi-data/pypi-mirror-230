import logging
from pathlib import Path

import typer
import yaml
from ascend_io_cli.support import CliOptions, _defaults_file_name, print_response

app = typer.Typer(no_args_is_help=True, help='Work with CLI default values')


@app.command()
def show(ctx: typer.Context):
  """Show default values"""
  config_file = Path.home().joinpath('.ascend', 'cli-default.yml')
  logging.debug(f'Loading config file: {config_file}')
  with open(config_file, 'rt') as file:
    configuration = yaml.safe_load(file) or {}
    print_response(ctx, configuration)


@app.command()
def list(ctx: typer.Context):
  """List possible default values"""
  obj = CliOptions().__dict__.keys()
  print_response(ctx, [*obj])


@app.command()
def set(
    ctx: typer.Context,
    name: str = typer.Argument(..., help='Name of value'),
    value: str = typer.Argument(..., help='Value to set as default'),
):
  """Set default value"""
  config_file = _defaults_file_name()

  with open(config_file, 'rt') as file:
    configuration = yaml.safe_load(file) or {}
    configuration[name] = value
    with open(config_file, 'w') as out_file:
      yaml.dump(configuration, out_file, sort_keys=True)
      print_response(ctx, configuration)


@app.command()
def set_hostname(
    ctx: typer.Context,
    hostname: str = typer.Argument(..., help='Default hostname to use'),
):
  """Set default hostname"""
  set(ctx, 'hostname', hostname)


@app.command()
def unset(ctx: typer.Context, name: str = typer.Argument(..., help='Name of value')):
  """Remove default value"""
  config_file = _defaults_file_name()

  with open(config_file, 'rt') as file:
    configuration = yaml.safe_load(file) or {}
    old_value = configuration.pop(name, None)
    if old_value:
      with open(config_file, 'w') as out_file:
        yaml.dump(configuration, out_file, sort_keys=True)
        print_response(ctx, configuration)
