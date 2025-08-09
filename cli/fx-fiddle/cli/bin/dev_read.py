#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .dev_read_d import dev_read_d


@click.group()
def dev_read():
    """Device memory read operations"""
    pass


dev_read.add_command(dev_read_d, name='d')