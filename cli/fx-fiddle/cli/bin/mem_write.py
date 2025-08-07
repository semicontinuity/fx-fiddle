#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .mem_write_d import mem_write_d


@click.group()
def mem_write():
    """Memory write operations"""
    pass


mem_write.add_command(mem_write_d, name='d')