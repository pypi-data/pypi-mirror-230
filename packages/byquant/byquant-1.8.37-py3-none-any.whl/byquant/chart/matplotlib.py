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

import matplotlib.pyplot as plt

def line(data={},x=[],y=[],label='',xlabel='',ylabel=''):
    if len(data) > 0:
        #return sns.lineplot(data=data, label=label)
        data.plot(label=label)  # 使用label参数指定线的标签
        plt.legend()  # 添加图例
        #plt.show()  # 显示图形
        #plt.close()
    else:
        plt.plot(x, y)  # 使用plot()方法设置x和y值
        if xlabel != '':
            plt.ylabel(xlabel)  # 设置y轴标签
        else:
            plt.xlabel('ByQuant.com')
        if ylabel == '':
            ylabel = label
        if ylabel != '':
            plt.ylabel(ylabel)  # 设置y轴标签
            
def scatter(x=[],y=[], marker='v', color='r', label=''):
    return plt.scatter(x=x, y=y, marker=marker, color=color, label=label)
        
def show():
    return plt.show()

def close():
    return plt.close()
    
def legend():
    return plt.legend()

def title(title_str):
    return plt.title(title_str)

def xlabel(xlabel_str):
    return plt.xlabel(xlabel_str)
    
def ylabel(ylabel_str):
    return plt.ylabel(ylabel_str)


