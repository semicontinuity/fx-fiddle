import click

option_port = click.option(
    "--port",
    default='/dev/ttyUSB0',
    type=str,
    help="Serial port device",
)
