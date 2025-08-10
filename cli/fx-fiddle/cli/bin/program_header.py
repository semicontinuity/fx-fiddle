#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .program_header_read import program_header_read


@click.group("header")
def program_header():
    """Commands for program header operations."""
    pass


program_header.add_command(program_header_read)