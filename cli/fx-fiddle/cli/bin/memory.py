#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .memory_read import memory_read
from .memory_write import memory_write


@click.group()
def memory():
    """Device memory operations"""
    pass


memory.add_command(memory_read, name='read')
memory.add_command(memory_write, name='write')