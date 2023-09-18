#!/usr/bin/env python
# -*-coding:utf-8-*-

import pytest
from pywander.unique_key import mapping_string
from pywander.str import random_string_generator
from collections import defaultdict
from pywander.list import double_iter


@pytest.mark.skip(reason="i have test it")
def test_mapping_string():
    data = defaultdict(lambda: 0)

    for i in range(100000):
        s = random_string_generator()

        c = mapping_string(s)

        data[c] += 1

    values = list(data.values())

    for i, j in double_iter(values):
        assert i == pytest.approx(j, rel=0.1)
