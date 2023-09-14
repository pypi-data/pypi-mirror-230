import functools

import pytest
import pandas as pd
import torch

import tdfl
import utils

devices = [torch.device("cpu")]
if torch.cuda.is_available():
    devices.append(torch.device("cuda"))
if torch.backends.mps.is_available() and torch.backends.mps.is_built():
    devices.append(torch.device("mps"))


@pytest.mark.parametrize(
    'df0_long',
    [
        (2, 100, 3, 'abc', 20),
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    'groupby',
    [
        'a',
        'b',
        'c',
        'd',
        ['b', 'c'],
        ['c', 'd'],
        ['b', 'c', 'd'],
    ],
)
@pytest.mark.parametrize(
    'columns, func, kwargs',
    [
        ('a', 'mean', None),
        ('d', 'sum', None),
        ('c', 'count', None),
        ('a', 'var', None),
        ('a', 'std', None),
        ('a', 'sem', None),
        ('a', 'min', None),
        ('a', 'max', None),
        ('a', ['mean', 'sum'], None),
        ('a', ['mean', 'sum'], {'hi': 'count'}), # xfail, cannot provide both
        ('a', None, {'hi': 'mean'}),
        ('a', None, {'hi': 'mean', 'bye': 'sum'}),
        ('a', None, None), # xfail, must provide something
        (None, None, {'hi': ('a', 'mean'), 'bye': ('d', 'sum'), 'byebye': ('c', 'count')}),
        (None, None, {'hi': ('a', 'mean')}),
        (None, None, None), # xfail, must provide something
    ]
)
@pytest.mark.parametrize('dropna', [True, False])
@pytest.mark.parametrize('sort', [True, False])
@pytest.mark.parametrize('device', devices)
def test_groupby_agg(df0_long, groupby, columns, func, kwargs, sort, dropna, device):
    if columns is None and func is not None:
        raise RuntimeError()

    if kwargs is None:
        kwargs = {}
    
    df, tdf = df0_long
        
    tg = tdf.groupby(groupby, sort=sort, dropna=dropna, device=device)
    g = df.groupby(groupby, as_index=False, sort=sort, dropna=dropna)

    if columns is None:
        output = functools.partial(tg.agg, **kwargs)
        expected = functools.partial(g.agg, **kwargs)
    else:
        output = functools.partial(tg[columns].agg, func=func, **kwargs)
        expected = functools.partial(g[columns].agg, func=func, **kwargs)
    
    def assert_equal(output, expected, sort=sort):
        output, expected = output.to_pandas(), expected.reset_index(drop=True)
        if not sort:
            output, expected = output.sort_values(list(output.columns)), expected.sort_values(list(expected.columns))
            output, expected = output.reset_index(drop=True), expected.reset_index(drop=True)
        pd.testing.assert_frame_equal(output, expected)
            
    utils.assert_equal_or_equal_error_type(output, expected, assert_equal)
