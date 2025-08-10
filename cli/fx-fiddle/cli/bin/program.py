#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .program_header import program_header
from .program_body import program_body


@click.group()
def program():
    """Commands for program operations."""
    pass


program.add_command(program_header)
program.add_command(program_body, name='body')