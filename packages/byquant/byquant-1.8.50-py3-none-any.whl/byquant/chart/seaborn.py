#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Author : Trabi
# Email : info@byquant.com
# Copyright (C) 2022-2023 ByQuant.com
#
#  ███████   ██    ██   ██████   ██    ██    ████    ██    ██  ████████  
#  ██    ██   ██  ██   ██    ██  ██    ██   ██  ██   ███   ██     ██     
#  ███████     ████    ██    ██  ██    ██  ████████  ██ ██ ██     ██         █████  █████  █████
#  ██    ██     ██     ██   ██   ██    ██  ██    ██  ██   ███     ██         █      █   █  █ █ █
#  ███████      ██      ███████   ██████   ██    ██  ██    ██     ██     ██  █████  █████  █ █ █
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from __future__ import (absolute_import, division, print_function,unicode_literals)
import seaborn as sns
#import pandas as pd
#def line(data,label):
#    return sns.lineplot(data=data, label=label)
    
def lineplot(data={},x=[],y=[],label=''):
    if len(data) > 0:
        return sns.lineplot(data=data, label=label)
    else:
        return sns.lineplot(x=x, y=y, label=label)
        
def jointplot(data={},x=[],y=[],label='', kind='reg', height=12):
    if len(data) > 0:
        return sns.jointplot(data=data, label=label)
    else:
        return sns.jointplot(x=x, y=y, kind='reg', height=12)
        
def histplot(data={},x=[],y=[],label='', kind='reg', height=12):
    if len(data) > 0:
        return sns.jointplot(data=data, label=label)
    else:
        return sns.jointplot(x=x, y=y, kind='reg', height=12)



