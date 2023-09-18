import collections
import functools
import numbers
import warnings

import torch
import numpy as np
import numpy.ma as ma

import hyclib as lib

def unpack_args(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        args = [arg.data if isinstance(arg, Array) else arg for arg in args]
        kwargs = {k: v.data if isinstance(v, Array) else v for k, v in kwargs.items()}
        return f(self, *args, **kwargs)
    return wrapper

def concat(arrs, dim=0):
    if len(arrs) == 0:
        raise ValueError(f"arrs must be at least length 1, but {len(arrs)=}.")

    is_tensor = [Array(arr).is_tensor for arr in arrs]
    if not lib.np.isconst(is_tensor):
        raise TypeError(f"Underlying data of arrs must either all be torch.Tensor or all be np.ndarray, but {is_tensor=}.")

    is_masked_array = [Array(arr).is_masked_array for arr in arrs]
    is_tensor = is_tensor[0]
    arrs = [arr.data for arr in arrs]
    
    if is_tensor:
        return Array(torch.cat(arrs, dim=dim))
    
    if any(is_masked_array):
        return Array(ma.concatenate(arrs, axis=dim))
    
    return Array(np.concatenate(arrs, axis=dim))

def stack(arrs, dim=0):
    if len(arrs) == 0:
        raise ValueError(f"arrs must be at least length 1, but {len(arrs)=}.")

    is_tensor = [Array(arr).is_tensor for arr in arrs]
    if not lib.np.isconst(is_tensor):
        raise TypeError(f"Underlying data of arrs must either all be torch.Tensor or all be np.ndarray, but {is_tensor=}.")

    is_masked_array = [Array(arr).is_masked_array for arr in arrs]
    is_tensor = is_tensor[0]
    arrs = [arr.data for arr in arrs]
    
    if is_tensor:
        return Array(torch.stack(arrs, dim=dim))
    
    if any(is_masked_array):
        return Array(ma.stack(arrs, axis=dim))
    
    return Array(np.stack(arrs, axis=dim))

class Array:
    def __init__(self, data):
        """
        A simple wrapper class that provides some unified operators for np.ndarray and torch.Tensor.
        This class is NOT meant to be used externally.
        Data is NOT copied upon construction (a shallow copy will be constructed if input is a list of objects)
        """
        writeable = True
        if isinstance(data, Array):
            _data, writeable = data.data, data.writeable
        elif isinstance(data, np.ndarray):
            _data, writeable = data, data.flags.writeable
        elif isinstance(data, torch.Tensor):
            _data = data
        elif (isinstance(data, collections.abc.Iterable) and isinstance(data, collections.abc.Sized)) and not isinstance(data, str):
            if all(isinstance(x, numbers.Number) for x in data):
                _data = np.array(data)
            else:
                _data = np.empty((len(data),), dtype=object)
                for i, data_i in enumerate(data):
                    _data[i] = data_i
        else:
            _data = np.array(data)

        self._data = _data
        self._is_tensor = isinstance(_data, torch.Tensor)
        self._device = _data.device if self.is_tensor else torch.device('cpu')
        self._is_masked_array = isinstance(_data, ma.MaskedArray)
        self._writeable = writeable
        
    @property
    def writeable(self):
        return self._writeable
    
    @writeable.setter
    def writeable(self, value):
        # Note: setting writeable to True is probably not a good idea, you probably want to create a copy instead.
        if not self._is_tensor:
            self._data.setflags(write=value)
        self._writeable = value
    
    @classmethod
    def empty(cls, shape, masked=True, is_tensor=False, dtype=None, device=None):
        if not is_tensor:
            if not (device is None or device.type == 'cpu'):
                raise ValueError(f"device must be None or 'cpu' when is_tensor is False, but {device=}")

            if masked:
                return cls(ma.array(np.empty(shape, dtype=dtype), mask=True, dtype=dtype))
            
            return cls(np.full(shape, np.nan, dtype=dtype))
        
        # TODO: return MaskedTensor if masked=True
        return cls(torch.full(shape, torch.nan, dtype=dtype, device=device))
        
    @property
    def data(self):
        return self._data
    
    @property
    def is_tensor(self):
        return self._is_tensor
    
    @property
    def is_masked_array(self):
        return self._is_masked_array
    
    @property
    def ndim(self):
        return self._data.ndim
    
    @property
    def shape(self):
        return self._data.shape
    
    @property
    def dtype(self):
        return self._data.dtype
    
    @property
    def nbytes(self):
        if self.is_tensor:
            return self.data.storage().nbytes()
        else:
            data = self.data
            while data.base is not None:
                data = data.base
            return data.nbytes
    
    @property
    def device(self):
        return self._device
    
    def __repr__(self):
        return f"Array({repr(self.data)})"
    
    def __str__(self):
        return f"Array({str(self.data)})"
    
    def __len__(self):
        return len(self.data)
    
    @unpack_args
    def __getitem__(self, key):
        if isinstance(key, torch.Tensor) and key.device != self.device:
            key = key.to(self.device)
            
        # key = Array(key).like(self, dtype=False) # convert to same object type as self.data and move to device if necessary
        arr = Array(self.data[key])

        if self.is_tensor and arr.data.storage().data_ptr() == self.data.storage().data_ptr():
            arr.writeable = self.writeable # same writeable flag since memory is shared
        return arr
    
    @unpack_args
    def __setitem__(self, key, value):
        if isinstance(key, torch.Tensor) and key.device != self.device:
            key = key.to(self.device)
        # key = Array(key).like(self, dtype=False) # convert to same object type as self.data and move to device if necessary
        if not self.writeable:
            raise ValueError("cannot call self.__setitem__ since self.writeable is set to False. Please copy Array first.")
        if self.is_tensor and isinstance(value, torch.Tensor):
            value = value.type(self.dtype) # pytorch bug on mps: tensor assignment is incorrect when value dtype is not the same as data dtype, see Github issue #95417. The fix has still not been merged into the release branch as of pytorch 2.0.1.
        self.data[key] = value
        
    def __iter__(self):
        yield from self.data
        
    @unpack_args
    def __add__(self, other):
        return Array(self.data + other)
    
    @unpack_args
    def __sub__(self, other):
        return Array(self.data - other)
    
    @unpack_args
    def __mul__(self, other):
        return Array(self.data * other)
        
    @unpack_args
    def __truediv__(self, other):
        return Array(self.data / other)
    
    @unpack_args
    def __pow__(self, other):
        return Array(self.data ** other)
    
    @unpack_args
    def __radd__(self, other):
        return Array(other + self.data)
    
    @unpack_args
    def __rsub__(self, other):
        return Array(other - self.data)
    
    @unpack_args
    def __rmul__(self, other):
        return Array(other * self.data)
        
    @unpack_args
    def __rtruediv__(self, other):
        return Array(other / self.data)
    
    @unpack_args
    def __rpow__(self, other):
        return Array(other ** self.data)

    @unpack_args
    def __eq__(self, other):
        return Array(self.data == other)

    @unpack_args
    def __ge__(self, other):
        return Array(self.data >= other)

    @unpack_args
    def __le__(self, other):
        return Array(self.data <= other)

    @unpack_args
    def __gt__(self, other):
        return Array(self.data > other)

    @unpack_args
    def __lt__(self, other):
        return Array(self.data < other)

    def __neg__(self):
        return Array(-self.data)
    
    def __invert__(self):
        return Array(~self.data)
    
    def any(self, dim=None):
        return Array(self.data.any(dim=dim)) if self.is_tensor else Array(self.data.any(axis=dim))
    
    def all(self, dim=None):
        return Array(self.data.all(dim=dim)) if self.is_tensor else Array(self.data.all(axis=dim))
    
    def nonzero(self):
        out = self.data.nonzero(as_tuple=True) if self.is_tensor else self.data.nonzero()
        return tuple(Array(out_i) for out_i in out)
    
    def astype(self, dtype):
        if self.is_tensor:
            if isinstance(dtype, str):
                dtype = getattr(torch, dtype)
            arr = Array(self.data.type(dtype))
            if arr.data.storage().data_ptr() == self.data.storage().data_ptr():
                arr.writeable = self.writeable # same writeable flag since memory is shared
        else:
            arr = Array(self.data.astype(dtype))
        
        return arr
    
    def asnumpy(self):
        """
        Coerces underlying tensor data to be np.ndarray. Underlying data is not copied.
        """
        if self.is_tensor:
            data = self.data.detach().cpu()
            arr = Array(data.numpy())
            if data.storage().data_ptr() == self.data.storage().data_ptr():
                writeable = self.writeable # same writeable flag since memory is shared (.numpy() does not copy data)
            return arr
        return self
    
    def asndarray(self):
        """
        Turns torch.tensor into regular np.ndarray and 
        turns ma.MaskedArray into regular np.ndarray by casting to nan-compatible dtype and then
        filling masked entries with nans.
        """
        arr = self.asnumpy()
        if arr.is_masked_array:
            data = arr.data
            data = data.astype(np.result_type(data.dtype, float)) # promote to at least float so we can turn masked elements to nan
            arr = Array(data.filled(np.nan))
        return arr
    
    def astensor(self):
        """
        Coerces underlying data to be torch.Tensor. Underlying data is not copied.
        """
        if self.is_tensor:
            return self
        arr = Array(torch.from_numpy(self.data))
        arr.writeable = self.writeable # same writeable flag since memory is shared (from_numpy() does not copy data)
        return arr

    @unpack_args
    def like(self, other, dtype=True, device=True):
        if self.is_tensor:
            # torch -> torch
            if isinstance(other, torch.Tensor):
                arr = self
                if dtype:
                    arr = arr.astype(other.dtype)
                if device:
                    arr = arr.to(other.device)
                 
            # torch -> numpy
            else:
                if not device and self.device.type != 'cpu':
                    raise ValueError(f"device must True if converting to np.ndarray and self is not on cpu, but {device=}.")
                    
                arr = self.detach().cpu().asnumpy()
                if dtype:
                    arr = arr.astype(other.dtype)
            
        else:
            # numpy -> torch
            if isinstance(other, torch.Tensor):
                arr = self.astensor()
                if dtype:
                    arr = arr.astype(other.dtype)
                if device:
                    arr = arr.to(other.device)
               
            # numpy -> numpy
            else:
                arr = self
                if dtype:
                    arr = arr.astype(other.dtype)
                
        return arr

    def copy(self):
        return Array(self.data.clone()) if self.is_tensor else Array(self.data.copy())
    
    def detach(self):
        if self.is_tensor:
            arr = Array(self.data.detach())
            arr.writeable = self.writeable # same writeable flag since memory is shared
        else:
            arr = self
        return arr
    
    def to(self, device, force=False):
        if device is None:
            return self
        
        if not isinstance(device, str):
            device = device.type
            
        arr = self.astensor() if force and device != 'cpu' else self
            
        if arr.is_tensor:
            if device == 'mps' and arr.dtype == torch.float64:
                if not force:
                    warnings.warn("Tensor column with dtype float64 was not moved to device since MPS does not support float64.", UserWarning)
                    return arr
                warnings.warn("Tensor column with dtype float64 converted to float32 since MPS does not support float64.", UserWarning)
                arr = arr.astype(torch.float32)
            new_arr = Array(arr.data.to(device))
            if new_arr.data.storage().data_ptr() == arr.data.storage().data_ptr():
                new_arr.writeable = arr.writeable # same writeable flag since memory is shared
            arr = new_arr
            
        return arr
    
    def cpu(self):
        return self.to('cpu')
    
    def numpy(self):
        return self.data.numpy() if self.is_tensor else self.data
    
    def tolist(self):
        return self.data.tolist()
    
    def broadcast_to(self, shape):
        if self.is_tensor:
            arr = Array(self.data.broadcast_to(shape))
            arr.writeable = False # not writeable after broadcasting, just like numpy
        else:
            arr = Array(np.broadcast_to(self.data, shape, subok=True)) # subok=False turns ma.MaskedArray into an np.ndarray
            if arr.is_masked_array:
                mask = np.broadcast_to(self.data.mask, shape) # mask is not automatically broadcasted, so we have to do it ourselves
                arr.data.mask = mask
        return arr
    
    def isna(self):
        if self.is_tensor:
            return Array(self.data.isnan())
        else:
            if self.data.dtype.kind == 'f':
                # if subok=True, na will be a masked array with the same mask as self.data,
                # so that setting na[self.data.mask] = True will modify the mask of self.data.
                # This caused a bug that was really difficult to diagnose
                na = np.isnan(self.data, subok=False)
            else:
                na = np.zeros(self.shape, dtype=bool)
            if self.is_masked_array:
                na[self.data.mask] = True
            return Array(na)
    
    def unique(self, sorted=True, return_index=False, return_inverse=False, return_counts=False, dim=None, equal_nan=False):
        if self.is_tensor:
            out = lib.pt.unique(self.data, sorted=sorted, return_index=return_index, return_inverse=return_inverse, return_counts=return_counts, dim=dim, equal_nan=equal_nan)
        elif self.is_masked_array:
            if not equal_nan:
                raise ValueError("equal_nan=True not supported for ma.MaskedArray")
            if return_counts:
                raise ValueError("return_counts=True not supported for ma.MaskedArray")
            if dim is not None:
                raise ValueError(f"only dim=None is supported for ma.MaskedArray, but {dim=}.")
            out = ma.unique(self.data, return_index=return_index, return_inverse=return_inverse)
        else:
            out = np.unique(self.data, return_index=return_index, return_inverse=return_inverse, return_counts=return_counts, axis=dim, equal_nan=equal_nan)
            
        if isinstance(out, tuple):
            return [Array(out_i) for out_i in out]
        return Array(out)
    
    # @unpack_args
    def bincount(self, weights=None, minlength=0, nan_policy='propagate'):
        weights = weights.data if isinstance(weights, Array) else weights
        if self.is_tensor:
            # arr = Array(self.data.bincount(weights=weights.data))
            ### torch.bincount derivative is not implemented as of torch==1.13.1, so use my custom bincount instead. ###
            arr = Array(lib.pt.bincount(self.data, weights=weights, minlength=minlength, nan_policy=nan_policy))
        else:
            x = self.data
            if self.is_masked_array:
                mask = x.mask
                x = x[~mask].data
                weights = weights[~mask]
                
            if isinstance(weights, ma.MaskedArray):
                weights = Array(weights).asndarray().data

            arr = Array(lib.np.bincount(x, weights=weights, minlength=minlength, nan_policy=nan_policy))
            
        return arr
    
    def argsort(self, descending=False, dim=-1):
        if self.is_tensor:
            return Array(self.data.argsort(descending=descending, dim=dim))
        else:
            arr = Array(np.argsort(self.data, axis=dim))
            if descending:
                arr = arr[::-1]
            return arr
        
    def bin(self, **kwargs):
        if self.is_tensor:
            out = lib.pt.stats.bin(self.data, nan_policy='omit', **kwargs)
        else:
            out = lib.sp.stats.bin(self.asndarray().data, nan_policy='omit', **kwargs)
            
        return [Array(out_i) for out_i in out]