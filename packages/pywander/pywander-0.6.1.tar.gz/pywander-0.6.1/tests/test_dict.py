#!/usr/bin/env python
# -*-coding:utf-8-*-

from pywander.dict import merge_dict


def test_merge_dict():
    x = {'a': 1, 'b': 2}
    y = {'b': 10, 'c': 11}
    res = merge_dict(x, y)
    assert res == {'a': 1, 'c': 11, 'b': 10}
