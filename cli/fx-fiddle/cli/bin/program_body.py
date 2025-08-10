#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Commands for program body operations.
"""

import click

from .program_body_read import program_body_read
from .program_body_write import program_body_write


@click.group()
def program_body():
    """Program body operations."""
    pass


program_body.add_command(program_body_read, name='read')
program_body.add_command(program_body_write, name='write')
