#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .mem_read import mem_read


@click.group()
def mem():
    """Memory operations"""
    pass


mem.add_command(mem_read, name='read')
