#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .dev_read import dev_read
from .dev_write import dev_write


@click.group()
def dev():
    """Device memory operations"""
    pass


dev.add_command(dev_read, name='read')
dev.add_command(dev_write, name='write')