#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .dev_write_d import dev_write_d


@click.group()
def dev_write():
    """Device memory write operations"""
    pass


dev_write.add_command(dev_write_d, name='d')