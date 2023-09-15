#!/usr/bin/env python3
import glob
import importlib
import os

import typer

from ascend_io_cli.support import (OutputFormat, hostname_callback, max_workers_callback, output_callback, verbosity_callback, verify_ssl_callback,
                                   access_token_callback)

# Loop through all commands and add them as sub-commands here.
app = typer.Typer(name='ascend')
for path in glob.glob(os.path.join(os.path.dirname(__file__), 'commands', '*.py')):
  name = os.path.basename(path)[:-3]
  if name != '__init__':
    module = importlib.import_module(f'ascend_io_cli.commands.{name}')
    app.add_typer(module.app, name=name)


@app.callback(no_args_is_help=True)
def app_callback(
    output: OutputFormat = typer.Option(None, show_default=False, callback=output_callback, help="The format", is_eager=True),
    verbosity: str = typer.Option(None, callback=verbosity_callback, help='Change verbosity of logging', is_eager=True),
    hostname: str = typer.Option(
        None,
        show_default=False,
        callback=hostname_callback,
        help='Hostname to use',
        is_eager=True,
    ),
    max_workers: int = typer.Option(10, callback=max_workers_callback, help='Maximum threads to use', is_eager=True),
    verify_ssl: bool = typer.Option(True, callback=verify_ssl_callback, is_eager=True, hidden=True, show_default=False),
    access_token: str = typer.Option(None, callback=access_token_callback, is_eager=True, hidden=True, show_default=False),
):
  pass


if __name__ == "__main__":
  app()
