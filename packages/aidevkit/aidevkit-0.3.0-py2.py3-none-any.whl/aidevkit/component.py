# -*-coding:utf-8 -*-
"""
:创建时间: 2023/7/30 17:36
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
from torch import nn


class MultiLayer(nn.Module):
    def __init__(
            self,
            layer_dim_list,
            bias=True,
            make_activation_function=lambda: nn.ReLU()
    ) -> None:
        super().__init__()
        layer_dim_group_list = [list(i) for i in zip(layer_dim_list[:-1], layer_dim_list[1:])]
        layer_list = [[nn.Linear(i[0], i[1], bias=bias), make_activation_function()] for i in layer_dim_group_list]
        self.module = nn.Sequential(*[j for i in layer_list for j in i])

    def forward(self, x):
        return self.module(x)


class GradientLayer(MultiLayer):
    def __init__(
            self,
            input_dim,
            layer_count,
            output_dim,
            bias=True,
            make_activation_function=lambda: nn.ReLU()
    ) -> None:
        weights = [i / layer_count for i in range(layer_count + 1)]
        if input_dim > output_dim:
            weights = [1 - ((1 - i) ** 2) for i in weights]
        else:
            weights = [i ** 2 for i in weights]
        layer_dim_list = [int(input_dim * (1 - t) + output_dim * t) for t in weights]
        layer_dim_list[0] = input_dim
        layer_dim_list[-1] = output_dim
        super().__init__(layer_dim_list, bias, make_activation_function)
