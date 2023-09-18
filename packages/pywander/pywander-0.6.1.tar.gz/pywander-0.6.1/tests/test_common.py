#!/usr/bin/env python
# -*-coding:utf-8-*-


from pywander.common import humanize_bytes, str2pyobj


def test_humanize_bytes():
    assert humanize_bytes(20200) == '19.7 KiB'

    assert humanize_bytes(1) == '1 B'
    assert humanize_bytes(1024) == '1.0 KiB'
    assert humanize_bytes(1024 * 123) == '123.0 KiB'
    assert humanize_bytes(1024 * 12342) == '12.1 MiB'
    assert humanize_bytes(1024 * 12342, 2) == '12.05 MiB'


def test_str2pyobj():
    x = str2pyobj('{"a":1}')
    assert isinstance(x, dict)

def test_config_read(sample_config):
    assert sample_config['a'] == 1