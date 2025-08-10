#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .program_header import program_header


@click.group()
def program():
    """Commands for program operations."""
    pass


program.add_command(program_header)