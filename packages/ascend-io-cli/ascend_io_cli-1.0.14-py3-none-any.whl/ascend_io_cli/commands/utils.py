import typer

import ascend_io_cli.commands.utils_commands.migration as migration

app = typer.Typer(help='Utilities', no_args_is_help=True)
app.add_typer(migration.app, name='migration')