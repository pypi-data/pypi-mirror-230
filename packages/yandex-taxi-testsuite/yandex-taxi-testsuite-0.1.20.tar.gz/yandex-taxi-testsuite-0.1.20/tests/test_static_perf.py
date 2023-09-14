import pytest

import pathlib

"""
orig: 200 passed in 9.96s
current vitek-oss: 200 passed in 0.57s
local: 200 passed in 0.32s
"""

_LIBS = [
    path / 'testsuite/static'
    for path in pathlib.Path(
        '/home/vitja/arcadia/taxi/uservices/libraries/'
    ).glob('*')
    if path.is_dir()
]


@pytest.fixture(scope='session')
def initial_data_path():
    return _LIBS + [
        '/tmp/xxx/',
    ]


@pytest.mark.parametrize('name', ['foo', 'bar'] * 100)
def test_it(name, get_file_path):
    for _ in range(10):
        get_file_path(name)
