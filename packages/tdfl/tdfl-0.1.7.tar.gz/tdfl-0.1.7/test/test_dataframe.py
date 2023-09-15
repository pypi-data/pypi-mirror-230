import functools

import pytest
import numpy as np
import pandas as pd
import torch

import tdfl
from tdfl import array as ar
import utils

devices = [torch.device("cpu")]
if torch.cuda.is_available():
    devices.append(torch.device("cuda"))
if torch.backends.mps.is_available() and torch.backends.mps.is_built():
    devices.append(torch.device("mps"))


@pytest.fixture
def xfail_cut(request):
    keys = ['right', 'bins']
    fixturevalues = {k: request.getfixturevalue(k) for k in keys}
    
    if fixturevalues['right'] and not isinstance(fixturevalues['bins'], pd.IntervalIndex):
        request.node.add_marker(pytest.mark.xfail(raises=NotImplementedError, strict=True, reason='Not Implemented'))


@pytest.mark.parametrize(
    'df0_long',
    [
        (3, 100, 3, 'abc', 20),
    ],
    indirect=True,
)
@pytest.mark.parametrize('column', ['a', 'c', 'd'])
@pytest.mark.parametrize(
    'bins',
    [
        pytest.param(5, marks=pytest.mark.xfail(raises=NotImplementedError, strict=True, reason='Not Implemented')),
        np.linspace(-2, 2, num=10),
        pd.interval_range(-2, 2, closed='left'),
        pytest.param(pd.interval_range(-2, 2, closed='right'), marks=pytest.mark.xfail(raises=NotImplementedError, strict=True, reason='Not Implemented')),
    ]
)
@pytest.mark.parametrize('right', [True, False])
@pytest.mark.parametrize(
    'labels',
    [
        None,
        False,
        pytest.param(['hi'], marks=pytest.mark.xfail(raises=NotImplementedError, strict=True, reason='Not Implemented')),
    ]
)
@pytest.mark.parametrize('retbins', [False, True])
@pytest.mark.parametrize('device', devices)
@pytest.mark.usefixtures('xfail_cut')
def test_cut(df0_long, column, bins, right, labels, retbins, device):
    tdf = df0_long.to(device)
    df = tdf.to_pandas()
    
    output = tdfl.cut(tdf[column], bins, right=right, labels=labels, retbins=retbins)
    expected = pd.cut(df[column], bins, right=right, labels=labels, retbins=retbins)

    if retbins:
        output, output_bins = output
        expected, expected_bins = expected
        if isinstance(expected_bins, pd.IntervalIndex):
            assert (output_bins == expected_bins).all()
        else:
            np.testing.assert_allclose(ar.Array(output_bins).detach().cpu().numpy(), expected_bins)

    if labels is None:
        expected = pd.IntervalIndex(expected).mid
    elif labels is False and isinstance(bins, pd.IntervalIndex):
        expected = expected.cat.codes.astype(float)
        expected[expected == -1] = np.nan

    np.testing.assert_allclose(ar.Array(output).detach().cpu().numpy(), expected.to_numpy())


@pytest.mark.parametrize(
    'ltdf, rtdf, on, left_on, right_on, suffixes, grads1, grads2',
    [
        ('df0', 'df1a', None, None, None, ('_x', '_y'), (True, True, False, True, True, True), (True, False, False, True, True, False)),
        ('df0', 'df1a', ('a', 'b'), None, None, ('_0', '_1'), (True, True, False, True, True, False, False, True), (True, False, False, True, True, False, False, False)),
        ('df0', 'df1b', None, None, None, ('_x', '_y'), (True, False, False, True, True, False, False), (True, False, False, True, True, False, False)),
        ('df0', 'df1b', None, ('a', 'b'), ('b', 'a'), ('_x', '_y'), (True, False, False, True, True, False, False, False, False), (True, False, False, True, True, False, False, False, False)),
    ],
)
@pytest.mark.parametrize(
    'how',
    [
        'inner',
        'left',
        'right',
        'outer',
    ],
)
@pytest.mark.parametrize('sort', [True, False])
@pytest.mark.parametrize('indicator', [True, False])
@pytest.mark.parametrize('device', devices)
def test_merge(request, ltdf, rtdf, on, left_on, right_on, suffixes, how, sort, indicator, grads1, grads2, device):
    print(f'{ltdf=}, {rtdf=}, {on=}, {left_on=}, {right_on=}, {suffixes=}, {how=}, {sort=}, {indicator=}')
    
    ltdf, rtdf = request.getfixturevalue(ltdf), request.getfixturevalue(rtdf)
    ldf, rdf = ltdf.to_pandas(), rtdf.to_pandas()

    ltdf, rtdf = ltdf.to(device), rtdf.to(device)

    tdf1 = ltdf.merge(rtdf, how=how, on=on, left_on=left_on, right_on=right_on, sort=sort, suffixes=suffixes, indicator=indicator)
    tdf2 = ltdf.merge(rdf, how=how, on=on, left_on=left_on, right_on=right_on, sort=sort, suffixes=suffixes, indicator=indicator)
    df = ldf.merge(rdf, how=how, on=on, left_on=left_on, right_on=right_on, sort=sort, suffixes=suffixes, indicator=indicator)

    if indicator:
        df['_merge'] = df['_merge'].astype(str)
    
    pd.testing.assert_frame_equal(tdf1.to_pandas(), df)
    pd.testing.assert_frame_equal(tdf2.to_pandas(), df)
    
    if indicator:
        assert len(tdf1.columns) == len(tdf2.columns) == len(grads1) + 1
    else:
        assert len(tdf1.columns) == len(tdf2.columns) == len(grads2)
        
    for v1, v2, grad1, grad2 in zip(tdf1.values(), tdf2.values(), grads1, grads2):
        if isinstance(v1, torch.Tensor):
            assert v1.requires_grad is grad1
        if isinstance(v2, torch.Tensor):
            assert v2.requires_grad is grad2


@pytest.mark.parametrize(
    'ltdf, rtdf, suffixes, grads',
    [
        ('df0', 'df1a', ('_x', '_y'), (True, False, False, True, True, False, True, False, False, True)),
        ('df0', 'df1b', ('_0', '_1'), (True, False, False, True, True, False, False, False, False)),
    ],
)
@pytest.mark.parametrize('sort', [True, False])
@pytest.mark.parametrize('indicator', [True, False])
@pytest.mark.parametrize('device', devices)
def test_merge_cross(request, ltdf, rtdf, suffixes, sort, indicator, grads, device):
    how = 'cross'
    
    ltdf, rtdf = request.getfixturevalue(ltdf), request.getfixturevalue(rtdf)
    ldf, rdf = ltdf.to_pandas(), rtdf.to_pandas()

    ltdf, rtdf = ltdf.to(device), rtdf.to(device)

    tdf = ltdf.merge(rtdf, how=how, sort=sort, suffixes=suffixes, indicator=indicator)
    df = ldf.merge(rdf, how=how, sort=sort, suffixes=suffixes, indicator=indicator)

    if indicator:
        df['_merge'] = df['_merge'].astype(str)

    pd.testing.assert_frame_equal(tdf.to_pandas(), df)
    for v, grad in zip(tdf.values(), grads):
        if isinstance(v, torch.Tensor):
            assert v.requires_grad == grad


@pytest.fixture
def xfail_groupby_agg(request):
    keys = ['func', 'device']
    allowed_failures = [
        ('min', torch.device('mps')),
        ('max', torch.device('mps')),
    ]
    fixturevalue = tuple(request.getfixturevalue(k) for k in keys)
    
    if fixturevalue in allowed_failures:
        request.node.add_marker(pytest.mark.xfail(raises=NotImplementedError, strict=True, reason='MPS bug'))


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
    'columns, func, kwargs, requires_grad',
    [
        ('a', 'mean', None, {'a'}),
        ('d', 'sum', None, set()),
        ('c', 'count', None, set()),
        ('a', 'var', None, {'a'}),
        ('a', 'std', None, {'a'}),
        ('a', 'sem', None, {'a'}),
        ('a', 'min', None, {'a'}),
        ('a', 'max', None, {'a'}),
        ('a', ['mean', 'sum'], None, {'mean', 'sum'}),
        ('a', ['mean', 'sum'], {'hi': 'count'}, None), # xfail, cannot provide both
        ('a', None, {'hi': 'mean'}, {'hi'}),
        ('a', None, {'hi': 'mean', 'bye': 'sum'}, {'hi', 'bye'}),
        ('a', None, None, None), # xfail, must provide something
        (None, None, {'hi': ('a', 'mean'), 'bye': ('d', 'sum'), 'byebye': ('c', 'count')}, {'hi'}),
        (None, None, {'hi': ('a', 'mean')}, {'hi'}),
        (None, None, None, None), # xfail, must provide something
    ]
)
@pytest.mark.parametrize('dropna', [True, False])
@pytest.mark.parametrize('sort', [True, False])
@pytest.mark.parametrize('device', devices)
@pytest.mark.usefixtures('xfail_groupby_agg')
def test_groupby_agg(df0_long, groupby, columns, func, kwargs, sort, dropna, device, requires_grad):
    if columns is None and func is not None:
        raise RuntimeError()

    if kwargs is None:
        kwargs = {}
    
    tdf = df0_long.to(device)
    df = tdf.to_pandas()
        
    tg = tdf.groupby(groupby, sort=sort, dropna=dropna, device=device)
    g = df.groupby(groupby, as_index=False, sort=sort, dropna=dropna)

    if columns is None:
        output = functools.partial(tg.agg, **kwargs)
        expected = functools.partial(g.agg, **kwargs)
    else:
        output = functools.partial(tg[columns].agg, func=func, **kwargs)
        expected = functools.partial(g[columns].agg, func=func, **kwargs)
    
    def assert_equal(output, expected, sort=sort, requires_grad=requires_grad):
        for k in requires_grad:
            assert output[k].requires_grad
        output, expected = output.to_pandas(), expected.reset_index(drop=True)
        if not sort:
            output, expected = output.sort_values(list(output.columns)), expected.sort_values(list(expected.columns))
            output, expected = output.reset_index(drop=True), expected.reset_index(drop=True)
        pd.testing.assert_frame_equal(output, expected)
            
    utils.assert_equal_or_equal_error_type(output, expected, assert_equal)
