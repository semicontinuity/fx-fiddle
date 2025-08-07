#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .mem_read import mem_read
from .mem_write import mem_write


@click.group()
def mem():
    """Memory operations"""
    pass


mem.add_command(mem_read, name='read')
mem.add_command(mem_write, name='write')
