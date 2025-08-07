#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .mem import mem


@click.group()
def cli():
    pass


cli.add_command(mem)


if __name__ == "__main__":
    cli()
