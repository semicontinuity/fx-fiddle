#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Commands for program body operations.
"""

import click

from .program_body_read import read


@click.group()
def program_body():
    """Program body operations."""
    pass


program_body.add_command(read, name='read')
