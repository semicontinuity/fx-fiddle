import sys

import click

from . import option_port
from ...lib.protocol import FxProtocol


@click.command()
@option_port
@click.option("--dry-run", is_flag=True, help="Print request to console only, don't send it")
@click.option("--verbose", is_flag=True, help="Print detailed information about the communication")
def program_body_write(
        port: str,
        dry_run: bool,
        verbose: bool,
):
    """Write program body to PLC memory from STDIN."""
    try:
        PROGRAM_START_ADDRESS = 0x805C

        value_list = read_hex_words_from_stdin()

        # Create protocol handler
        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            # Write flash memory
            protocol.write_flash(PROGRAM_START_ADDRESS, value_list)

            # If not dry run, display confirmation
            if not dry_run:
                print(f"Program body written to address 0x{PROGRAM_START_ADDRESS:X}:")
                for i, value in enumerate(value_list):
                    print(f"  [0x{PROGRAM_START_ADDRESS + i:X}]: {value} (0x{value:04X})")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


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
