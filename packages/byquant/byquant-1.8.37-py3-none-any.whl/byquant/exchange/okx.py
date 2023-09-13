#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Author : Trabi
# Copyright (C) 2022-2023 ByQuant.com
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

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
                        
from ccxt.okx import okx

class by_okx(okx):
        
    def describe(self):
        parent_describe = super(by_okx, self).describe()  # 调用父类的describe方法
        parent_options = parent_describe['options']  # 获取父类的options字典
        modified_options = self.deep_extend(parent_options, {
            'brokerId': 'f09cb09d13b0BCDE',  # Uakeey
        })
        new_describe = {
            'byapi': True,
            'options': modified_options,
        }
        return self.deep_extend(parent_describe, new_describe)  # 深度合并父类描述和自定义描述




