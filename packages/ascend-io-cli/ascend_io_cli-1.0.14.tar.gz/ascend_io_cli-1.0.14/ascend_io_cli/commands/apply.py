#!/usr/bin/env python3
from pathlib import Path

import typer
from ascend.sdk.applier import DataflowApplier, DataServiceApplier, ConnectionApplier, CredentialApplier, ComponentApplier

from ascend_io_cli.commands.clone import _hydrate_dataflow, _hydrate_data_service, _hydrate_credential, _hydrate_connection, _hydrate_component
from ascend_io_cli.support import get_client, print_response

app = typer.Typer(name='apply', help='Apply local changes to remote data service, dataflow, or component', no_args_is_help=True)


@app.command()
def credential(
    ctx: typer.Context,
    data_service_id: str = typer.Argument(..., help='Data Service id to push changes', show_default=False),  #
    name: str = typer.Argument(..., help='Name for credential to apply', show_default=False),
    credential_type: str = typer.Argument(..., help='Credential type: e.g ascend.mysql, mysql.custom.python...', show_default=False),
    details: str = typer.Argument(..., help='Location for credential', show_default=False),
):
  """
  Apply local changes to a credential.
  """
  client = get_client(ctx)

  creds_obj = _hydrate_credential(credential_id=name, credential_type=credential_type, credential_details=details)
  CredentialApplier(client).apply(data_service_id, creds_obj)
  print_response(ctx, {})


@app.command()
def connection(
    ctx: typer.Context,
    data_service_id: str = typer.Argument(None, help='Data Service id with changes', show_default=False),
    credential_id: str = typer.Argument(None, help='credential id associated with connection', show_default=False),
    name: str = typer.Argument(..., help="Name for connection", show_default=False),
    connection_type: str = typer.Argument(..., help="Credential type: e.g ascend.mysql, mysql.custom.python...", show_default=False),
    details: str = typer.Argument(..., help="Location for credential", show_default=False),
):
  """Apply local changes to a connection."""
  client = get_client(ctx)

  conn_obj = _hydrate_connection(connection_id=name, connection_type=connection_type, connection_details=details, credential_id=credential_id)
  ConnectionApplier(client).apply(data_service_id, conn_obj)
  print_response(ctx, conn_obj)


@app.command()
def component(
    ctx: typer.Context,
    data_service_id: str = typer.Argument(..., help='Data Service id with component changes', show_default=False),
    dataflow_id: str = typer.Argument(..., help='Dataflow id with component changes', show_default=False),
    component_id: str = typer.Argument(..., help='Component id to update', show_default=False),
    base_dir: str = typer.Option('./ascend', help='Base directory for the data service containing the component'),
    omit_data_service_dir: bool = typer.Option(False, help='Omit the data-service folder from the directory structure'),
    omit_dataflow_dir: bool = typer.Option(False, help='Omit the dataflow folder from the directory structure'),
    omit_component_dir: bool = typer.Option(False, help='Omit the component folder from the directory structure'),
):
  """Apply local changes to a component (read, write, or transform)"""
  client = get_client(ctx)

  base_dir = Path(base_dir).resolve()
  base_dir = base_dir if omit_data_service_dir else base_dir.joinpath(data_service_id)
  base_dir = base_dir if omit_dataflow_dir else base_dir.joinpath(dataflow_id)
  base_dir = base_dir if omit_component_dir else base_dir.joinpath('components')

  component_obj = _hydrate_component(data_service_id=data_service_id, dataflow_id=dataflow_id, component_id=component_id, base_dir=str(base_dir))
  ComponentApplier(client, {}).apply(data_service_id, dataflow_id, component_obj)
  print_response(ctx, component_obj)


@app.command()
def dataflow(
    ctx: typer.Context,
    data_service_id: str = typer.Argument(..., help='Data Service id containing dataflow to apply', show_default=False),
    dataflow_id: str = typer.Argument(..., help='Dataflow id to apply', show_default=False),
    new_data_service: str = typer.Option(None, help='Apply this dataflow as a dataflow within this service'),
    new_dataflow: str = typer.Option(None, help='Apply this dataflow as a dataflow with this name'),
    base_dir: str = typer.Option('./ascend', help='Base directory containing the dataflow'),
    omit_data_service_dir: bool = typer.Option(False, help='Omit the data-service folder from the directory structure'),
    omit_dataflow_dir: bool = typer.Option(False, help='Omit the dataflow folder from the directory structure'),
):
  """Apply local changes to a data flow to the target host. The default flow location is will be '<base-dir>/<data-service>/<dataflow>' """

  client = get_client(ctx)

  base_dir = Path(base_dir).resolve()
  base_dir = base_dir if omit_data_service_dir else base_dir.joinpath(data_service_id)
  base_dir = base_dir if omit_dataflow_dir else base_dir.joinpath(dataflow_id)

  flow = _hydrate_dataflow(data_service_id=data_service_id,
                           dataflow_id=dataflow_id,
                           new_data_service_id=new_data_service if new_data_service else data_service_id,
                           new_dataflow_id=new_dataflow if new_dataflow else dataflow_id,
                           base_dir=str(base_dir))
  DataflowApplier(client).apply(data_service_id=new_data_service if new_data_service else data_service_id, dataflow=flow)
  print_response(ctx, flow)


@app.command()
def data_service(
    ctx: typer.Context,
    data_service_id: str = typer.Argument(..., help='Data Service id with changes to apply', show_default=False),
    new_data_service_id: str = typer.Option(None, help='A new Data Service id to push these changes to', show_default=False),
    base_dir: str = typer.Option('./ascend', help='Base directory containing the flow'),
    omit_data_service_dir: bool = typer.Option(False, help='Omit the data-service folder from the directory structure'),
):
  """Apply local changes to a data service to the target host. The default location is will be '<base-dir>/<data-service>' """
  client = get_client(ctx)
  base_dir = Path(base_dir).resolve()
  base_dir = base_dir if omit_data_service_dir else base_dir.joinpath(data_service_id)
  data_service_obj = _hydrate_data_service(data_service_id=data_service_id,
                                           new_data_service_id=new_data_service_id if new_data_service_id else data_service_id,
                                           base_dir=str(base_dir))
  DataServiceApplier(client).apply(data_service=data_service_obj)
  print_response(ctx, data_service_obj)


if __name__ == "__main__":
  app()
