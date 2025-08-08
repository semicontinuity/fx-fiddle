#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .mem import mem
from .bit import bit


@click.group()
def cli():
    pass


cli.add_command(mem)
cli.add_command(bit)


if __name__ == "__main__":
    cli()
