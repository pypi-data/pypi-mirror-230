import typer
import base64
from .broker.brokers import app as broker_app
from .cloud.cloud_cli import app as cloud_app
from rich import print

app = typer.Typer(help="""
Welcome to RemotiveLabs CLI - Simplify and automate tasks for cloud resources and brokers
""")


app.add_typer(broker_app, name="broker", help="Manage a single broker - local or cloud")
app.add_typer(cloud_app, name="cloud", help="Manage resources in RemotiveCloud", )
