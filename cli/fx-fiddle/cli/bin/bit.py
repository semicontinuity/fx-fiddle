#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bit operations for the FX3U PLC.
"""

import click

from .bit_set import bit_set
from .bit_clear import bit_clear


@click.group()
def bit():
    """Bit operations"""
    pass


bit.add_command(bit_set, name='set')
bit.add_command(bit_clear, name='clear')