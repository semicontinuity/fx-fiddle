#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .mem import mem
from .bit import bit
from .flash import flash
from .dev import dev


@click.group()
def cli():
    pass


cli.add_command(mem)
cli.add_command(bit)
cli.add_command(flash)
cli.add_command(dev)


if __name__ == "__main__":
    cli()
