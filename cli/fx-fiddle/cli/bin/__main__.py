#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .bit import bit
from .flash import flash
from .param import param
from .memory import memory


@click.group()
def cli():
    pass


cli.add_command(bit)
cli.add_command(flash)
cli.add_command(param)
cli.add_command(memory)


if __name__ == "__main__":
    cli()
