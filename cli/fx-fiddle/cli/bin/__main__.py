#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .bit import bit
from .flash import flash
from .dev import dev
from .param import param


@click.group()
def cli():
    pass


cli.add_command(bit)
cli.add_command(flash)
cli.add_command(dev)
cli.add_command(param)


if __name__ == "__main__":
    cli()
