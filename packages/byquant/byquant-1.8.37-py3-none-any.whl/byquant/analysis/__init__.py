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

from .byanalysis import *

def show(datadict,out='',warn = False):
    if datadict['freqo'] == '1d':
        return Analysis(datadict,out=out,warn = warn).show()
    else:
        print('Only Support Daily Freq')
    
def returns(datadict,out='',warn = False):
    if datadict['freqo'] == '1d':
        return Analysis(datadict,out=out,warn = warn).returns()
    else:
        print('Only Support Daily Freq')
        
def position(datadict,out='',warn = False):
    return Analysis(datadict,out=out,warn = warn).position()

    
def trading(datadict,out='',warn = False):
    return Analysis(datadict,out=out,warn = warn).trading()
    
def trip(datadict,out='',warn = False):
    if datadict['freqo'] == '1d':
        return Analysis(datadict,out=out,warn = warn).trip()
    else:
        print('Only Support Daily Freq')
    
    