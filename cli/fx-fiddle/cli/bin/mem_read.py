#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .mem_read_d import mem_read_d


@click.group()
def mem_read():
    """Memory read operations"""
    pass


mem_read.add_command(mem_read_d, name='d')
