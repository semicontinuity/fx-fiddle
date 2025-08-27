import sys

import click

option_port = click.option(
    "--port",
    default='/dev/ttyUSB0',
    type=str,
    help="Serial port device",
)


def read_hex_words_from_stdin():
    # Read values from STDIN
    value_list = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            try:
                value = int(line, 16)  # Parse as hex
                if value < 0 or value > 0xFFFF:
                    raise ValueError("Value must be between 0x0000 and 0xFFFF")
                value_list.append(value)
            except ValueError as e:
                click.echo(f"Error parsing value '{line}': {str(e)}", err=True)
                sys.exit(1)
    if not value_list:
        click.echo("Error: No values provided via STDIN", err=True)
        sys.exit(1)
    return value_list
