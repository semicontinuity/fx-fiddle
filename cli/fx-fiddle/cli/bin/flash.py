#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flash memory operations for the FX3U PLC.
"""

import click


@click.group()
def flash():
    """Flash memory operations"""
    pass


from .flash_lock import flash_lock
from .flash_read import flash_read
from .flash_write import flash_write


flash.add_command(flash_lock, name='lock')
flash.add_command(flash_read, name='read')
flash.add_command(flash_write, name='write')
