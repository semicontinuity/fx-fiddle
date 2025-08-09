#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .param_read import param_read
from .param_write import param_write


@click.group()
def param():
    """Parameter operations"""
    pass


param.add_command(param_read, name='read')
param.add_command(param_write, name='write')