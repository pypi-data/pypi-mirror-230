import typer
from typing import List
from .lib.broker import Broker

app = typer.Typer(help=help)

@app.command()
def start(
        filename: str = typer.Argument(..., help="Path to local file to upload"),
        namespace: List[str] = typer.Option(..., help="Namespace to record"),
        url: str = typer.Option(..., help="Broker URL", envvar='REMOTIVE_BROKER_URL'),
        api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token",
                                    envvar='REMOTIVE_BROKER_API_KEY')
):
    broker = Broker(url, api_key)
    broker.record_multiple(namespace, filename)


@app.command()
def stop(
        filename: str = typer.Argument(..., help="Path to local file to upload"),
        namespace: List[str] = typer.Option(..., help="Namespace to record"),
        url: str = typer.Option(..., help="Broker URL", envvar='REMOTIVE_BROKER_URL'),
        api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token",
                                    envvar='REMOTIVE_BROKER_API_KEY')
):
    broker = Broker(url, api_key)
    broker.stop_multiple(namespace, filename)
    print("Successfully stopped recording")