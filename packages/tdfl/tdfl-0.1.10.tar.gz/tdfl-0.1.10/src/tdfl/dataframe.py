import collections
import re
import logging
import sys
import warnings
import html
import functools

import torch
from torch import mps
import numpy as np
import numpy.ma as ma
import pandas as pd
from pandas.io.formats import printing
from pandas.core.reshape.tile import _infer_precision, _round_frac
from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution
from bs4.formatter import HTMLFormatter

import hyclib as lib

from . import array as ar
from . import (
    parsing,
    options,
    utils,
)

logger = logging.getLogger(__name__)

__all__ = ['NA', 'InternalError', 'DataFrame', 'DataFrameGroupBy', 'ColumnGroupBy', 'concat', 'cut']

NA = ma.masked

class InternalError(Exception):
    pass
    
def _is_0d_col_idx(obj):
    return isinstance(obj, collections.abc.Hashable) or (isinstance(obj, np.ndarray) and obj.ndim == 0) or (isinstance(obj, torch.Tensor) and obj.ndim == 0)

def _is_1d_col_idx(obj):
    return isinstance(obj, list) or isinstance(obj, slice) or (isinstance(obj, np.ndarray) and obj.ndim == 1) or (isinstance(obj, torch.Tensor) and obj.ndim == 1)

def _is_0d_row_idx(obj):
    return isinstance(obj, int) or (isinstance(obj, np.ndarray) and obj.ndim == 0) or (isinstance(obj, torch.Tensor) and obj.ndim == 0)

def _is_1d_row_idx(obj):
    return isinstance(obj, list) or isinstance(obj, slice) or (isinstance(obj, np.ndarray) and obj.ndim == 1) or (isinstance(obj, torch.Tensor) and obj.ndim == 1)

def _extract(out, df, column, idx_column, df2=None, column2=None, idx_column2=None):
    if isinstance(df[column], torch.Tensor):
        new = torch.zeros(len(out), dtype=df[column].dtype, device=df[column].device)
    elif df2 is not None and isinstance(df2[column2], torch.Tensor):
        new = torch.zeros(len(out), dtype=df2[column2].dtype, device=df2[column2].device)
    else:
        raise RuntimeError()
        
    values, idx = df[column], out[idx_column]
    if isinstance(df, pd.DataFrame):
        values = values.to_numpy()
    isnan = np.isnan(idx)
    values = values[idx[~isnan].astype(int)]
    if not isinstance(values, torch.Tensor):
        values = torch.from_numpy(values).type(new.dtype).to(new.device)
    new[~isnan] = values
    
    if df2 is not None:
        values, idx2 = df2[column2], out[idx_column2]
        if isinstance(df2, pd.DataFrame):
            values = values.to_numpy()
        isnan2 = np.isnan(idx2)
        values = values[idx2[~isnan2].astype(int)]
        if not isinstance(values, torch.Tensor):
            values = torch.from_numpy(values).type(new.dtype).to(new.device)
        new[~isnan2] = values
        
        isnan = isnan & isnan2

    if np.count_nonzero(isnan) > 0:
        new = new.float()
        new[isnan] = np.nan
    return new

def _get_key(k, df, suffix):
    # Helper function in DataFrame.merge
    k_df, k_in_df = None, False
    if k in set(df.keys()):
        k_df = k
        k_in_df = True
    else:
        k_ = k.removesuffix(suffix)
        if k_ in set(df.keys()):
            k_df = k_
            k_in_df = True
    return k_df, k_in_df
    
class DataFrame:
    def __init__(self, data, columns=None, copy=True):
        """
        Initialize a DataFrame with the given data and columns.
        Data is stored in the .data attribute and is a dictionary of ar.Array representing the columns.
        If copy is True, constructs a copy of data (arrays and tensor are copied, but for objects, only references are copied).
        Otherwise, only dictionary references (if data is a dictionary) are copied.
        
        When indexing:
            - an element is returned as a 0d torch.Tensor, 0d np.ndarray, or object
            - a column is returned as a 1d torch.Tensor or np.ndarray
            - a row is returned as a dictionary of 0d torch.Tensor, 0d np.ndarray, or object
            - a sub-frame is returned as a DataFrame

        :param data: a 2D np.ndarray/torch.Tensor, a list/dictionary of (0/1D torch.Tensor/np.ndarray or any other object), or a DataFrame
        :param columns: a list of column names (optional)
        """
        if columns is not None:
            if not ((isinstance(columns, collections.abc.Iterable) and isinstance(columns, collections.abc.Sized)) or isinstance(columns, np.ndarray) or isinstance(columns, torch.Tensor)):
                raise TypeError(f"columns must be None or be a sized iterable, but {type(columns)=}.")
                
            if len(set(columns)) != len(columns):
                raise ValueError(f"Columns must be unique, but detected duplicates in {columns}.")
                
        if isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], dict):
                data = {k: v for k, *v in lib.itertools.dict_zip(*data, mode='strict')}
            
            else:
                _columns = range(len(data)) if columns is None else columns

                if len(_columns) != len(data):
                    raise ValueError(f"length of columns must be same as length of data, but {len(_columns)=} and {len(data)=}.")

                data = {k: v for k, v in zip(_columns, data)}
                columns = None
        
        if isinstance(data, dict):
            if columns is not None:
                raise ValueError(f"columns must be None when data is a dictionary, but {type(columns)=}.")

            arrs, shapes = [], []
            for v in data.values():
                arr = ar.Array(v)
                if arr.ndim > 1:
                    raise ValueError(f"data must be at most 1D, but {arr.ndim=}.")
                    
                arrs.append(arr)
                shapes.append(arr.shape)
                
            shape = np.broadcast_shapes(*shapes)
            
            if copy:
                data = {k: v.broadcast_to(shape).copy() for k, v in zip(data.keys(), arrs)}
            else:
                data = {k: v.broadcast_to(shape) for k, v in zip(data.keys(), arrs)}
            
        elif isinstance(data, DataFrame):
            if columns is not None:
                raise ValueError(f"column must be None when data is a DataFrame, but {type(columns)=}.")
                
            if copy:
                data = {k: v.copy() for k, v in data._items()}
            else:
                data = data._data.copy() # dictionary shallow copy
            
        elif isinstance(data, np.ndarray) or isinstance(data, torch.Tensor):
            if data.ndim != 2:
                raise ValueError(f"data must be 2D if it is a np.ndarray or torch.Tensor, but {data.ndim=}.")
                
            if columns is None:
                columns = range(data.shape[1])

            if len(columns) != data.shape[1]:
                raise ValueError(f"Number of columns must be the second dim of data, but {len(columns)=}, {data.shape[1]=}.")
            
            data = ar.Array(data)
            if copy:
                data = data.copy()
            data = {column: data[:,i] for i, column in enumerate(columns)}
        
        else:
            raise TypeError(f"data must be a 2D list/np.ndarray/torch.Tensor, a dictionary of (0/1D torch.Tensor/np.ndarray or any other object), or a DataFrame, but got {type(data)}.")
                
        self._data = data
        
    @classmethod
    def empty(cls, N_rows, dtype=None, is_tensor=False, device=None, columns=None, masked=True):
        if dtype is None:
            dtype = float
        if device is None:
            device = 'cpu'
        
        dtype = np.atleast_1d(dtype)
        is_tensor = np.atleast_1d(is_tensor)
        device = np.atleast_1d(device)
        
        dtype, is_tensor, device = np.broadcast_arrays(dtype, is_tensor, device)
        
        if columns is not None and len(columns) != len(dtype):
            raise ValueError("length of columns is incompatible with other provided arguments.")
            
        data = [ar.Array.empty((N_rows,), dtype=dt, is_tensor=it, device=dv, masked=masked) for dt, it, dv in zip(dtype, is_tensor, device)]
        
        return cls(data, columns=columns, copy=False)
    
    @classmethod
    def empty_like(cls, df, N_rows=None, masked=True):
        if N_rows is None:
            N_rows = len(df)
            
        info = df.info()
        
        return cls.empty(N_rows, dtype=info['dtype'], is_tensor=info['is_tensor'], device=info['device'], columns=info['column'], masked=masked)
        
    def _validate(self):
        lengths = {}
        for column, data in self._items():
            if not isinstance(ar.Array):
                raise InternalError(f"column data must be ar.Array, but {type(arr)=}.")
            if not data.ndim == 1:
                raise InternalError(f"column data must be 1D, but {data.ndim=}.")
            lengths[column] = len(series)

        if not lib.np.isconst(lengths.values()):
            raise InternalError(f"each column must have the same length, but {lengths=}.")
        
    @property
    def columns(self):
        return list(self._data.keys())
    
    def __len__(self):
        if len(self._data) == 0:
            return 0
        return len(next(iter(self._data.values())))
    
    @property
    def shape(self):
        return (len(self), len(self._data))
    
    def keys(self):
        yield from self._data.keys()
        
    def _values(self):
        yield from self._data.values()
    
    def values(self):
        for v in self._data.values():
            yield v.data
            
    def _items(self):
        yield from self._data.items()
    
    def items(self):
        for k, v in self._data.items():
            yield k, v.data
        
    def __iter__(self):
        for i in range(len(self)):
            yield self[:,i]
     
    @property
    def dtype(self):
        return {k: v.dtype for k, v in self._items()}
    
    @property
    def device(self):
        return {k: v.device if v.is_tensor else None for k, v in self._items()}
    
    @property
    def is_tensor(self):
        return {k: v.is_tensor for k, v in self._items()}
    
    @property
    def nbytes(self):
        return {k: v.nbytes for k, v in self._items()}

    def __getitem__(self, key):
        """
        Index the DataFrame as if indexing a 2D array with arr[:, col_idx][row_idx], where key = (col_idx, row_idx).
        Returns a 0d array if both col_idx and row_idx are 0d, a list of 0d elements if row_idx is 0d,
        a 1d np.ndarray/torch.Tensor if col_idx is 0d, and a dataframe if neither is 0d.
        Note that it is different from indexing a 2D array with arr[col_idx, row_idx] when both col_idx and row_idx are array-like.
        col_idx can only be a slice if it is slice(None) or slice(None, None, step), since it would introduce 
        ambiguity as to whether to interpret slice.start and slice.end as column indices or as column names.
        
        There is no need to worry about making row_idx the same object type and device as column (this would be impossible if
        indexing multiple columns with different object types and devices) - Array.__getitem__ takes care of this issue.
        """
        if isinstance(key, tuple):
            col_idx, row_idx = key
        else:
            col_idx, row_idx = key, slice(None)
            
        if col_idx is Ellipsis:
            col_idx = slice(None)
            
        if row_idx is Ellipsis:
            row_idx = slice(None)
        
        if _is_0d_col_idx(col_idx):
            return self._data[col_idx][row_idx].data
        
        if _is_1d_col_idx(col_idx):
            if isinstance(col_idx, slice):
                if col_idx.start is not None or col_idx.stop is not None:
                    raise ValueError(f"col_idx can only be a slice if both start and end are None, but {col_idx=}")
                    
                col_idx = self.columns[col_idx]

            if _is_0d_row_idx(row_idx):
                return [self._data[k][row_idx].data for k in col_idx]
            
            if _is_1d_row_idx(row_idx):
                return DataFrame({k: self._data[k][row_idx].data for k in col_idx}, copy=False)
            
            raise TypeError(f"Invalid row index {type(row_idx)=}.")

        raise TypeError(f"Invalid column index {type(col_idx)=}.")
        
    def _set_column(self, column, row_idx, arr):
        # NOTE: row_idx = None produces different behavior than row_idx = slice(None)
        # even though both sets all elements of a column
        if row_idx is None:
            self._data[column] = arr.broadcast_to(len(self))
        else:
            if not column in self.columns:
                self._data[column] = ar.Array.empty(
                    (len(self),),
                    is_tensor=arr.is_tensor,
                    dtype=arr.dtype,
                    device=arr.device,
                )
            if not self._data[column].writeable:
                self._data[column] = self._data[column].copy()
            if self._data[column].is_tensor:
                arr = arr.astensor() # allow setting tensor elements with np array
            self._data[column][row_idx] = arr
        
    def __setitem__(self, key, value):
        """
        Set elements of the DataFrame. One can understand it abstractly as doing
        arr.T[col_idx, :][row_idx] = value, where key = (col_idx, row_idx), except
        for two major differences:
            1) In numpy this assignment would not modify the array, but here it would.
            2) In numpy the value is broadcasted to the correct shape by adding leading batch dimensions,
               but here the value is broadcasted to the correct shape by adding trailing batch dimensions.
               
        There is no need to worry about making row_idx the same object type and device as column (this would be impossible if
        indexing multiple columns with different object types and devices) - Array.__setitem__ takes care of this issue.
        """
        if isinstance(key, tuple):
            col_idx, row_idx = key
        else:
            col_idx, row_idx = key, None
            
        if col_idx is Ellipsis:
            col_idx = slice(None)
            
        if row_idx is Ellipsis:
            row_idx = slice(None)
            
        value = ar.Array(value)
        
        if _is_0d_col_idx(col_idx):
            self._set_column(col_idx, row_idx, value)
            
        elif _is_1d_col_idx(col_idx):
            if isinstance(col_idx, slice):
                if col_idx.start is not None or col_idx.stop is not None:
                    raise ValueError(f"col_idx can only be a slice if both start and end are None, but {col_idx=}")
                    
                col_idx = self.columns[col_idx]

            # broadcast value to (len(col_idx), ...) so that we can iterate over columns.
            # this broadcasting different form the usual numpy broadcasting rule in that 
            # batch dimensions here are TRAILING not leading.
            if value.ndim <= 1:
                value = value.broadcast_to(len(col_idx))
            elif value.ndim == 2:
                value = value.broadcast_to((len(col_idx), -1))
            else:
                raise ValueError(f"value must be at most 2D, but {value.ndim=}")
                
            for k, v in zip(col_idx, value):
                self._set_column(k, row_idx, ar.Array(v))
    
    def __repr__(self):
        return repr(self.to_pandas())
        
    def copy(self):
        # Should work similarly to pd.DataFrame.copy(deep=True)
        return DataFrame(self._data, copy=True)
    
    def torch(self):
        df = DataFrame(self, copy=False)
        for k, v in df._items():
            df[k] = v.astensor()
        return df
        
    def to(self, device):
        for k, v in self._items():
            self[k] = v.to(device)
        return self
    
    def to_list(self):
        """
        Returns data as a list of columns. Data is copied (but non-array objects are not copied).
        """
        return list(self.copy().values())
    
    def to_dict(self):
        """
        Returns data as a dict of columns. Data is copied (but non-array objects are not copied).
        """
        return self.copy()._data
    
    def as_dict(self):
        """
        Returns data as a dict of columns. Data is not copied (only a shallow dict copy is performed).
        """
        return self._data.copy()
    
    def to_numpy(self):
        """
        Returns data as a 2D np.ndarray. Data is copied (but non-array objects are not copied).
        """
        return np.stack([v.detach().cpu().numpy() for v in self._values()], axis=1) # np.stack returns copy
    
    def to_tensor(self, device=None):
        """
        Returns data as a 2D torch.Tensor, but may raise error if there is a column with a datatype
        that is not supported by pytorch. Data is copied (but non-array objects are not copied).
        """
        return torch.stack([v.astensor().data.to(device) for v in self._values()], dim=1)
    
    def to_pandas(self, copy=True):
        """
        Returns data as a pd.DataFrame.
        """
        return pd.DataFrame({k: v.detach().cpu().numpy() for k, v in self._items()}, copy=copy)

    # def to_html(self, *args, **kwargs):
    #     return self.to_pandas(copy=False).to_html(*args, **kwargs)

    def _repr_html_(self):
        """
        For automatic pretty table rendering in jupyter by calling display(df)
        """
        return self.to_html(
            min_rows=options.display.min_rows,
            max_rows=options.display.max_rows,
            show_dimensions=options.display.show_dimensions,
        )
    
    def to_html(self, min_rows=None, max_rows=None, show_dimensions=False, formatters=None, float_format=None, show_column_info=True, na_rep='NaN'):
        """
        chatGPT-assisted code. Slightly slower than using the pd.DataFrame.to_html,
        but allows for more control over display detail, since we don't need to convert
        torch.Tensor to np.ndarray.
        """
        if float_format is None:
            precision = options.display.precision
            float_format = lambda x: utils.trim_zeros_single_float(
                f"{x: .{precision:d}f}"
            )

        N = len(self)
        M = len(self.columns)
        
        if max_rows is None:
            max_rows = np.inf
        if min_rows is None:
            min_rows = N

        if N <= max_rows:
            row_indices = np.r_[:N]
        else:
            n_top = min_rows // 2
            n_bottom = min_rows - n_top - 1
            row_indices = np.r_[:n_top, -1, N - n_bottom:N]
        
        html_str = '<table border="1" class="dataframe"><thead><tr style="text-align: right;">'
        html_str += "<th></th>"
        
        for column in self.columns:
            if show_column_info:
                is_tensor, dtype, device = self._data[column].is_tensor, str(self._data[column].dtype), self._data[column].device
                otype = 'torch' if is_tensor else 'numpy'
                search = re.search('.*\.(.*)', dtype)
                dtype = dtype if search is None else search.group(1)
                device = 'cpu' if device is None else str(device)
                header = [html.escape(s) for s in [column, otype, dtype, device]]
            else:
                header = [html.escape(column)]
            html_str += f"<th>{'<br/>'.join(header)}</th>"
        html_str += "</tr></thead><tbody>"
        
        for idx in row_indices:
            if idx == -1:
                html_str += "<tr><th>...</th>"
                html_str += "<td>...</td>" * M
                html_str += "</tr>"
            else:
                html_str += "<tr>"
                html_str += f"<th>{idx}</th>"
                for column in self.columns:
                    cell = self[column][idx]
                    if formatters is not None and column in formatters:
                        cell = formatters[column](cell)
                    else:
                        if na_rep is not None and (
                            (pd.api.types.is_scalar(cell) and pd.isna(cell)) or
                            (isinstance(cell, torch.Tensor) and cell.isnan())
                        ):
                            # see https://github.com/pandas-dev/pandas/blob/v2.0.1/pandas/io/formats/format.py#L1390
                            try:
                                # try block for np.isnat specifically
                                # determine na_rep if x is None or NaT-like
                                if cell is None:
                                    cell = "None"
                                elif cell is pd.NA:
                                    cell = str(pd.NA)
                                elif cell is pd.NaT or np.isnat(cell):
                                    cell = "NaT"
                                else:
                                    cell = na_rep
                            except (TypeError, ValueError):
                                # np.isnat only handles datetime or timedelta objects
                                cell = na_rep
                        elif isinstance(cell, (float, np.floating)) or (isinstance(cell, torch.Tensor) and cell.is_floating_point()):
                            cell = float_format(cell.item()).strip(' ')
                        elif isinstance(cell, torch.Tensor):
                            cell = str(cell.item())
                        else:
                            # see https://github.com/pandas-dev/pandas/blob/v2.0.1/pandas/io/formats/format.py#L1383
                            cell = str(functools.partial(
                                printing.pprint_thing,
                                escape_chars=("\t", "\r", "\n"),
                                quote_strings=False,
                            )(cell))
                    html_str += f"<td>{html.escape(cell)}</td>"
                html_str += "</tr>"
        html_str += "</tbody></table>"
        
        if show_dimensions == 'truncate':
            show_dimensions = N > max_rows
        if show_dimensions:
            html_str += f"<p>{N} rows × {M} columns</p>"
        
        html_formatter = HTMLFormatter(entity_substitution=EntitySubstitution.substitute_html, indent=2)
        soup = BeautifulSoup(html_str, 'html.parser', preserve_whitespace_tags=['th', 'td', 'p'])
        return soup.prettify(formatter=html_formatter).strip('\n').replace('&times;', '×')
    
    def _to_numpy_numeric(self):
        arrs = []
        for arr in self._values():
            arr = arr.detach().cpu().numpy() # do everything in numpy due to various torch.unique bugs
            if arr.dtype.kind not in 'biufc': # non-numeric
                _, arr = np.unique(arr, return_inverse=True)
            if isinstance(arr, ma.MaskedArray):
                arr = arr.astype(np.result_type(arr.dtype, float)) # promote to at least float so we can turn masked elements to nan
                arr[arr.mask] = np.nan
                arr = arr.data # drop mask, turns ma.MaskedArray into np.ndarray
            arrs.append(arr)
        arr = np.stack(arrs, axis=-1)
        return arr
    
    def _to_numeric(self):
        info = self.info()
        is_tensor = any(info['is_tensor'])
        gpu_device_types = {device.type for device in info['device'] if device.type != 'cpu'}
        if len(gpu_device_types) > 1:
            raise ValueError(f"_to_numeric expects only one type of gpu device, but found {gpu_device_types=}.")
        device = gpu_device_types.pop() if len(gpu_device_types) == 1 else 'cpu'
        
        if device == 'mps' and any(arr.dtype == torch.float64 or arr.dtype == np.float64 for arr in self._values()):
            device = 'cpu' # currently cannot move float64 tensors to MPS 
            
        arrs = []
        for arr in self._values():
            if not arr.is_tensor and arr.dtype.kind not in 'biufc': # non-numeric
                _, arr = arr.unique(return_inverse=True, equal_nan=True)
            if is_tensor:
                arr = arr.astensor()
            arr = arr.to(device)
            arrs.append(arr)
        arr = ar.stack(arrs, dim=-1)
        
        return arr
    
    def info(self):
        return DataFrame([{
            'column': k,
            'n_rows': len(v), # should be same for every column
            'is_tensor': v.is_tensor,
            'dtype': v.dtype,
            'device': v.device,
            'nbytes': v.nbytes,
        } for k, v in self._items()])
    
    def __delitem__(self, columns):
        columns = np.atleast_1d(columns)
        for column in columns:
            del self._data[column]
    
    def drop(self, *columns, copy=False):
        df = DataFrame(self, copy=copy)
        for column in columns:
            del df[column]
        return df
    
    def rename(self, kwargs, copy=False):
        return DataFrame({kwargs.get(k, k): self._data[k] for k in self._data}, copy=copy) # preserves order
    
    def groupby(self, *args, **kwargs):
        # Should works similarly to pd.DataFrame.groupby(by, as_index=False)
        return DataFrameGroupBy(self, *args, **kwargs)
    
    def eval(self, condition, level=0):
        condition = parsing.preparse(condition)
        var_names = parsing.parse_var_names(condition)
        frame = sys._getframe(level+1) # see https://github.com/pandas-dev/pandas/blob/main/pandas/core/computation/scope.py
        env = frame.f_globals | frame.f_locals
        
        # add @ variables
        var_dict = {f'{parsing.LOCAL_TAG}{k}': env[k] for k in var_names}
        
        # add dataframe columns
        var_dict = var_dict | {parsing.clean_column_name(k): v.data for k, v in self._data.items() if not isinstance(k, int)}
        
        return eval(condition, var_dict)
    
    def query(self, condition, level=0):
        return self[:,self.eval(condition, level=level+1)]
    
    # def merge(self, df, how='inner', on=None, left_on=None, right_on=None, suffixes=('_x', '_y')):
    #     """
    #     Note on efficiency: For i such that left_on[i] != right_on[i], this function returns both left_on[i] and right_on[i]
    #     resulting in increased memory usage. So for best performance, rename the columns you want to merge so that
    #     left_on[i] == right_on[i] for all i before merging.
    #     """
    #     # if not isinstance(df, DataFrame):
    #     #     raise TypeError(f"df must be a DataFrame, but {type(df)=}.")
        
    #     if how == 'cross':
    #         raise NotImplementedError()
        
    #     if on is not None:
    #         if not (left_on is None and right_on is None):
    #             raise ValueError(f"left_on and right_on must be None when on is not None, but {left_on=}, {right_on=}.")
    #         left_on, right_on = on, on
            
    #     if (left_on is None and right_on is not None) or (left_on is not None and right_on is None):
    #         raise ValueError(f"left_on and right_on must either be both None or not None, but {left_on=}, {right_on=}.")
        
    #     if left_on is None: # right_on must also be None
    #         on = [column for column in self.columns if column in df.columns] # same order as left df
    #         left_on, right_on = on, on
    #     else:
    #         left_on, right_on = np.atleast_1d(left_on), np.atleast_1d(right_on)
    #         if len(left_on) != len(right_on):
    #             raise ValueError(f"Length of left_on must be same as length of right_on, but {len(left_on)=}, {len(right_on)=}.")
          
    #     combined = concat([self[left_on], df[right_on].rename({r: l for l, r in zip(left_on, right_on)})])._to_numpy_numeric()
    #     larr, rarr = combined[:len(self)], combined[len(self):]
        
    #     larr, linv, lcount = lib.np.unique_rows(larr, sorted=False, return_inverse=True, return_counts=True)
    #     rarr, rinv, rcount = lib.np.unique_rows(rarr, sorted=False, return_inverse=True, return_counts=True)

    #     _, larr_idx, rarr_idx = lib.np.intersect_rows(larr, rarr, assume_unique=True, return_indices=True)

    #     lmask, rmask = np.isin(linv, larr_idx), np.isin(rinv, rarr_idx)

    #     lindices, rindices = lmask.nonzero()[0], rmask.nonzero()[0]

    #     inv_larr_idx, inv_rarr_idx = np.empty(len(larr), dtype=int), np.empty(len(rarr), dtype=int)
    #     inv_larr_idx[larr_idx] = np.arange(len(larr_idx))
    #     inv_rarr_idx[rarr_idx] = np.arange(len(rarr_idx))

    #     lindices, rindices = lindices[np.argsort(inv_larr_idx[linv[lmask]])], rindices[np.argsort(inv_rarr_idx[rinv[rmask]])]

    #     lcount, rcount = lcount[larr_idx], rcount[rarr_idx]

    #     lindices = np.repeat(lindices, np.repeat(rcount, lcount))
    #     rindices = lib.np.repeat(rindices, lcount, chunks=rcount)
        
    #     on = [column for column in left_on if column in right_on]
    #     left_not_on = [column for column in self.columns if column not in on]
    #     right_not_on = [column for column in df.columns if column not in on]
        
    #     left, middle, right = self[left_not_on, lindices], self[on, lindices], df[right_not_on, rindices]
        
    #     if how in ['left', 'outer']:
    #         left = concat([self[left_not_on, ~lmask], left])
    #         middle = concat([self[on, ~lmask], middle])
    #         right = concat([DataFrame.empty_like(right, N_rows=(~lmask).sum()), right])
            
    #     if how in ['right', 'outer']:
    #         left = concat([left, DataFrame.empty_like(left, N_rows=(~rmask).sum())])
    #         middle = concat([middle, df[on, ~rmask]])
    #         right = concat([right, df[right_not_on, ~rmask]])
            
    #     left_rename = {column: f'{column}{suffixes[0]}' for column in left.columns if column in right.columns}
    #     right_rename = {column: f'{column}{suffixes[1]}' for column in right.columns if column in left.columns}

    #     return concat([left.rename(left_rename), middle, right.rename(right_rename)], axis=1)

    def merge(self, right, how='inner', on=None, left_on=None, right_on=None, sort=False, suffixes=('_x', '_y'), indicator=False, validate=None):
        """
        Same as pd.DataFrame.merge, except that if two tensor columns are 
        merged together, require that both are on the same device and raise
        error if both requires gradient. If one of them requires gradient,
        then data is taken from that column. Otherwise, data is taken from the
        left dataframe. Also forbids column names '__left_idx__' and '__right_idx__',
        and the '_merge' column is a str array rather than a category array since
        right now we don't support pandas ExtensionArrays.
        """
        if '__left_idx__' in self:
            raise ValueError("self cannot contain column named '__left_idx__'.")
            
        if  '__right_idx__' in right:
            raise ValueError("right cannot contain column named '__right_idx__'.")

        if isinstance(right, DataFrame):
            right_pd = right.to_pandas()
            right_is_tensor = right.is_tensor
        elif isinstance(right, pd.DataFrame):
            right_pd = right.copy(deep=False)
            right_is_tensor = {k: False for k in right.columns}
        else:
            raise TypeError("right must be a tdfl.DataFrame or pd.DataFrame.")
        
        left_pd = self.to_pandas()
        left_is_tensor = self.is_tensor
        
        left_pd['__left_idx__'] = np.arange(len(left_pd))
        right_pd['__right_idx__'] = np.arange(len(right_pd))
        out = DataFrame({k: v.to_numpy() for k, v in left_pd.merge(right_pd, how=how, on=on, left_on=left_on, right_on=right_on, sort=sort, suffixes=suffixes, indicator=indicator, validate=validate).items()})

        for k in out.keys():
            k_left, k_in_left = _get_key(k, self, suffixes[0])
            k_right, k_in_right = _get_key(k, right, suffixes[1])

            if k_in_left and k_in_right:
                if left_is_tensor[k_left] and right_is_tensor[k_right]:
                    both = ~np.isnan(out['__left_idx__']) & ~np.isnan(out['__right_idx__'])
                    if self[k_left].requires_grad and right[k_right].requires_grad and np.count_nonzero(both) > 0:
                        raise ValueError((
                            f"Merged columns {k_left} and {k_right} both have gradient "
                            "information and there are rows which come from both, "
                            "therefore cannot be merged."
                        ))
                    if self[k_left].device != right[k_right].device:
                        raise ValueError((
                            f"Merged columns {k_left} and {k_right} must be on the same device, "
                            f"but got {self[k_left].device} and {right[k_right].device}."
                        ))
                if left_is_tensor[k_left]:
                    out[k] = _extract(out, right, k_right, '__right_idx__', self, k_left, '__left_idx__')
                elif right_is_tensor[k_right]:
                    out[k] = _extract(out, self, k_left, '__left_idx__', right, k_right, '__right_idx__')
            elif k_in_left and left_is_tensor[k_left]:
                out[k] = _extract(out, self, k_left, '__left_idx__')
            elif k_in_right and right_is_tensor[k_right]:
                out[k] = _extract(out, right, k_right, '__right_idx__')
                
        del out['__left_idx__'], out['__right_idx__']
        return out

def cut(arr, bins, right=True, labels=None, precision=3, retbins=False):
    """
    Analogue of pd.cut, except that when labels is None, it returns
    the midpoints of intervals since pd.ExtensionArrays are not currently supported.
    Also pd.cut ignores the labels argument when bins is pd.IntervalIndex,
    but here it doesn't.
    """
    if labels is not None and labels is not False:
        raise NotImplementedError("Currently only supports labels=None or labels=False.")
    
    if right and not isinstance(bins, pd.IntervalIndex):
        raise NotImplementedError("Currently only implemented for right=False.")
    
    if isinstance(bins, pd.IntervalIndex):
        if bins.closed != 'left':
            raise NotImplementedError("Currently only implemented for bins closed on the left.")
        left, right = bins.left.to_numpy(), bins.right.to_numpy()
        if not (left[1:] == right[:-1]).all():
            raise NotImplementedError(f"cut is currently only defined for contiguous bins, but got {bins=}.")
        _bins = np.concatenate([left, right[-1:]])
    elif isinstance(bins, int):
        raise NotImplementedError("Currently does not support integer bins argument.")
    else:
        _bins = bins
    
    arr = ar.Array(arr)
    binnums, centers, edges = arr.bin(bins=_bins)
    binnums[arr == edges[-1]] = len(edges)

    # round to precision, see https://github.com/pandas-dev/pandas/blob/v2.1.0/pandas/core/reshape/tile.py#L588
    # I'm assuming this is important to prevent floating point precision issues when performing groupby.
    _edges = edges.detach().cpu().numpy()
    precision = _infer_precision(precision, _edges)
    _edges = ar.Array([_round_frac(_edge, precision) for _edge in _edges])
    _edges = _edges.like(edges)
    centers[1:-1] = (_edges[:-1] + _edges[1:])/2
    centers[0] = np.nan
    centers[-1] = np.nan
    
    if labels is None:
        out = [centers[binnums].data]
    else:
        if binnums.is_tensor:
            binnums = binnums.astype('float32')
        else:
            binnums = binnums.astype('float64')
        binnums[binnums == 0] = np.nan
        binnums[binnums == len(edges)] = np.nan
        out = [(binnums - 1).data]

    if retbins:
        if isinstance(bins, pd.IntervalIndex):
            out += [bins]
        else:
            out += [edges.data]
        
    if len(out) == 1:
        return out[0]
    
    return out
    
class DataFrameGroupBy:
    def __init__(self, df, by, sort=True, dropna=True, nanstats=True, device=None):
        if not nanstats:
            warnings.warn("nanstats=False is currently untested. Use at your own risk.", UserWarning)
        
        self.df = df
        self.by = np.atleast_1d(by)
        self.dropna = dropna
        self.nanstats = nanstats
        data = self.df[self.by]
        
        if len(data.columns) == 0:
            raise ValueError("No selected columns.")

        if not self.dropna:
            # Perform unique in numpy since it supports equal_nan=True
            arr = data._to_numpy_numeric() # numeric numpy array representation of selected columns
            _, idx, inv_idx = lib.np.unique_rows(arr, sorted=sort, return_index=True, return_inverse=True) # faster than np.unique
            # _, idx, inv_idx = np.unique(arr, return_index=True, return_inverse=True, axis=0)
            self._groups = DataFrame({column: self.df[column][idx] for column in self.by})
            # self._na = np.stack([arr.isna().detach().cpu().numpy() for arr in self._groups._values()], axis=1).any(axis=1)
            # self._row_to_group_idx = ar.Array(inv_idx)
            self._na = DataFrame({k: v.isna() for k, v in self._groups._items()})._to_numeric().any(dim=1)
            self._row_to_group_idx = ar.Array(inv_idx).like(self._na, dtype=False)

        else:
            # no need for equal_nan=True, so we can perform unique in pytorch if possible
            arr = data._to_numeric().to(device, force=True) # numeric array representation of selected columns
            if arr.is_masked_array:
                arr = arr.asndarray() # ma.MaskedArray currently does not support unique
            _, idx, inv_idx = arr.unique(sorted=sort, return_index=True, return_inverse=True, dim=0) # equal_nan=False
            self._groups = DataFrame({column: self.df._data[column][idx] for column in self.by})
            # self._na = np.stack([arr.isna().asndarray() for arr in self._groups._values()], axis=1).any(axis=1)
            # self._row_to_group_idx = inv_idx.asndarray()
            self._na = DataFrame({k: v.isna() for k, v in self._groups._items()})._to_numeric().any(dim=1)
            self._row_to_group_idx = inv_idx
        
        self._group_indexer = GroupIndexer(self)
        
    @property
    def groups(self):
        if self.dropna:
            return self._groups[:,~self._na.data]
        return self._groups
    
    @property
    def group(self):
        return self._group_indexer
    
    def items(self):
        for i, group in enumerate(self.groups):
            yield group, self.group[i]
            
    def __getitem__(self, key):
        if isinstance(key, list):
            raise NotImplementedError()
        
        return ColumnGroupBy(self, key)
        
    def agg(self, **kwargs):
        """
        Equivalent to pd.DataFrameGroupBy.agg with as_index=False.
        """
        if len(kwargs) == 0:
            raise TypeError("Must provide keyword arguments with tuples of (column, aggfunc).")
        
        column_kwargs = collections.defaultdict(list)  # dict[in_column, list[tuple[order, tuple[out_column, func]]]]
        for i, (out_column, v) in enumerate(kwargs.items()):
            if not (isinstance(v, tuple) and len(v) == 2):
                raise TypeError(f"v must be a 2-tuple of (column, aggfunc), but {v=}.")
                
            in_column, func = v
            column_kwargs[in_column].append((i, (out_column, func)))
        
        results = {}
        orders = {}
        for in_column, kwargs in column_kwargs.items():
            order, kwargs = zip(*kwargs)  # list[order], list[tuple[out_column, func]]
            result = self[in_column]._agg_without_groups(**dict(kwargs))  # tdfl.Dataframe, dict[out_column, agged]
            order = dict(zip(result.keys(), order))  # dict[out_column, order]
                
            results |= result
            orders |= order
            
        results = {k: results[k] for k, _ in sorted(orders.items(), key=lambda item: item[1])}
        return DataFrame(self.groups.as_dict() | results)
    
class ColumnGroupBy:
    def __init__(self, dfgb, column):
        self._row_to_group_idx = dfgb._row_to_group_idx
        self._groups = dfgb._groups
        self._na = dfgb._na
        self.groups = dfgb.groups
        self.dropna = dfgb.dropna
        self.nan_policy = 'omit' if dfgb.nanstats else 'propagate'
        self.df = dfgb.df
        self.column = column
        self.data = dfgb.df[column]
        
    def _agg(self, func, results):
        if func in results:
            return results[func]

        _row_to_group_idx = self._row_to_group_idx.like(self.data, dtype=False)
        
        # See scipy.stats.binned_statistic_dd for reference
        if func == 'count':
            weights = (~ar.Array(self.data).isna()).astype('int64').data
            result = _row_to_group_idx.bincount(weights=weights, nan_policy=self.nan_policy)
            result = result.astype('int64')
        
        elif func == 'sum':
            result = _row_to_group_idx.bincount(weights=self.data, nan_policy=self.nan_policy)
        
        elif func == 'mean':
            result = self._agg('sum', results) / self._agg('count', results)
            
        elif func == 'var':
            count, mean = self._agg('count', results), self._agg('mean', results)
            result = (_row_to_group_idx.bincount(
                weights=(self.data - mean[_row_to_group_idx].data)**2,
                nan_policy=self.nan_policy
            )) / (count - 1)
            result[count == 0] = np.nan # count == 1 are already nans since we divided by count - 1
            
        elif func == 'std':
            var = self._agg('var', results)
            result = var**0.5
        
        elif func == 'sem':
            count, std = self._agg('count', results), self._agg('std', results)
            result = std / count**0.5
        
        elif func == 'min':
            v = ar.Array(self.data)
            if v.is_tensor and v.device.type == 'mps':
                raise NotImplementedError("Aggregrate function 'min' not implemented for the case when the aggregated column is on device MPS due to MPS bug where __setitem__ is non-deterministic even though pytorch is set to use determinisitc algorithms. See Github issue #97574.")
            
            if self.nan_policy == 'propagate':
                i = (-v).argsort() # same as descending=True but NaNs are at the end
            else:
                i = v.argsort(descending=True)
            result = ar.Array.empty((len(self._groups),), masked=False, is_tensor=v.is_tensor, dtype=v.dtype, device=v.device)
            
            # In pytorch calling __setitem__ with an index tensor that has duplicate elements is undefined and non-deterministic by                 # default. See the documentation on index_put_. In my own experiments, setting use_deterministic_algorithms resolves this               # issue and makes pytorch behave the same way as numpy, but I don't think this behavior is gauranteed.
            if set_enabled := v.is_tensor and not torch.are_deterministic_algorithms_enabled():
                torch.use_deterministic_algorithms(True)
            result[_row_to_group_idx[i]] = v[i]
            if set_enabled:
                torch.use_deterministic_algorithms(False)
        
        elif func == 'max':
            v = ar.Array(self.data)
            if v.is_tensor and v.device.type == 'mps':
                raise NotImplementedError("Aggregrate function 'min' not implemented for the case when the aggregated column is on device MPS due to MPS bug where __setitem__ is non-deterministic even though pytorch is set to use determinisitc algorithms. See Github issue #97574.")
            
            if self.nan_policy == 'omit':
                i = (-v).argsort(descending=True) # same as descending=False but NaNs are at the front
            else:
                i = v.argsort()
            result = ar.Array.empty((len(self._groups),), masked=False, is_tensor=v.is_tensor, dtype=v.dtype, device=v.device)
            
            # In pytorch calling __setitem__ with an index tensor that has duplicate elements is undefined and non-deterministic by                 # default. See the documentation on index_put_. In my own experiments, setting use_deterministic_algorithms resolves this               # issue and makes pytorch behave the same way as numpy, but I don't think this behavior is gauranteed.
            if set_enabled := v.is_tensor and not torch.are_deterministic_algorithms_enabled():
                torch.use_deterministic_algorithms(True)
            result[_row_to_group_idx[i]] = v[i] 
            if set_enabled:
                torch.use_deterministic_algorithms(False)
        
        elif callable(func):
            v = ar.Array(self.data)
            result = ar.Array.empty((len(self._groups),), masked=False, is_tensor=v.is_tensor, dtype=v.dtype, device=v.device)
            for idx, group in enumerate(self._groups):
                result[idx] = func(v[_row_to_group_idx == idx].data)
        
        else:
            raise ValueError(f"func must be a callable or a string in ['count', 'sum', 'mean', 'var', 'std', 'sem', 'min', 'max'], but got {func}")
        return result

    def _agg_without_groups(self, func=None, **kwargs):
        if func is None and len(kwargs) == 0:
            raise TypeError("Must provide 'func' or named aggregation **kwargs.")

        if func is not None and len(kwargs) > 0:
            raise TypeError("Must not provide both 'func' and named aggregation **kwargs.")

        if isinstance(func, list):
            kwargs = {v if isinstance(v, str) else v.__name__: v for v in func}
        elif func is not None:
            kwargs = {self.column: func}
        
        results = {}
        for k, v in kwargs.items():
            results[k] = self._agg(v, results)

        results = {k: v[~self._na].data if self.dropna else v.data for k, v in results.items()}

        return DataFrame(results)
    
    def agg(self, *args, **kwargs):
        result = self._agg_without_groups(*args, **kwargs).as_dict()
        # I have to do this stupid for-loop because pandas has a bizarre column order
        # when groupby columns and agg columns overlap. For instance,
        # groupby(['b', 'c']).agg(a=(), b=()) results in column order ['c', 'a', 'b']
        groups = {k: v for k, v in self.groups.items() if k not in result.keys()}
        return DataFrame({**groups, **result})
    
class GroupIndexer:
    def __init__(self, groupby):
        self.groupby = groupby
        self.columns = [column for column in groupby.df.columns if column not in groupby.by]
        if groupby.dropna:
            self.idx_map = (~groupby._na).nonzero()[0]
        
    def __getitem__(self, idx):
        if self.groupby.dropna:
            idx = self.idx_map[idx]
            
        return self.groupby.df[self.columns, self.groupby._row_to_group_idx.data == idx]
        
def concat(dfs, axis=0):
    assert len(dfs) > 0
    all_columns = [df.columns for df in dfs]
    
    if axis == 0:
        if not lib.np.isconst(all_columns, axis=0).all():
            raise ValueError(f"dfs must have the same columns when axis=0, but {all_columns=}.")
            
        columns = all_columns[0]
        return DataFrame({column: ar.concat([df._data[column] for df in dfs]) for column in columns})
    
    elif axis == 1:
        columns = lib.itertools.flatten_seq(all_columns)
        if len(set(columns)) != len(columns):
            raise ValueError(f"dfs must have non-overlapping columns when axis=1, but {all_columns=}.")
            
        return DataFrame({k: v for df in dfs for k, v in df.items()})
    
    raise ValueError("axis must be 0 (concatenate along rows) or 1 (concatenate along columns)")
