import collections
import contextlib
import itertools

import torch

__all__ = ['isconst', 'inv_perm', 'lexsort', 'unique', 'meshgrid', 'use_deterministic_algorithms']

def isconst(x, dim=None, **kwargs):
    x = torch.as_tensor(x)
    
    if dim is None:
        x = x.reshape(-1)
    else:
        if isinstance(dim, int):
            dim = [dim]
        if len(dim) == 0:
            return torch.ones(x.shape, device=x.device, dtype=torch.bool)
        dim = sorted([d % x.ndim for d in dim])[::-1]
        for d in dim:
            x = torch.movedim(x, d,-1)
        x = x.reshape(*x.shape[:-len(dim)],-1)
        
    if x.is_floating_point():
        return torch.isclose(x[...,:-1], x[...,1:], **kwargs).all(dim=-1)
    return (x[...,:-1] == x[...,1:]).all(dim=-1)

def inv_perm(x):
    x_inv = torch.empty_like(x)
    x_inv[x] = torch.arange(len(x), device=x.device)
    return x_inv

def lexsort(keys, dim=-1):
    keys = keys if isinstance(keys, torch.Tensor) else torch.stack(keys)
    if keys.ndim < 2:
        raise ValueError(f"keys must be at least 2 dimensional, but {keys.ndim=}.")
    if len(keys) == 0:
        raise ValueError(f"Must have at least 1 key, but {len(keys)=}.")
    
    # to understand reasoning, see the code at
    # https://github.com/wouterkool/attention-learn-to-route/blob/master/utils/lexsort.py#L39-L48
    idx = keys[0].argsort(dim=dim, stable=True)
    for k in keys[1:]:
        idx = idx.gather(dim, k.gather(dim, idx).argsort(dim=dim, stable=True))
    
    return idx

def _unique_sorted(x, dim=None, return_index=False, return_inverse=False, return_counts=False, first_index=True):
    if dim is None:
        x = x.reshape(-1)
        dim = 0
        
    # reshape to a 2D tensor where we compute unique rows
    x = x.movedim(dim, 0)
    shape = x.shape
    x = x.reshape(shape[0], -1)
    
    sort_idx = lexsort(x.t().flip(0)) # note: as of torch.2.0.0 there is a bug with torch.flip on MPS
    x = x[sort_idx]
    
    if return_index:
        x, inverse, counts = torch.unique_consecutive(x, dim=0, return_inverse=True, return_counts=True)
        tot_counts = torch.cat((counts.new_zeros(1), counts.int().cumsum(dim=0).long()))[:-1] # cast to int32 due to MPS limitation
        index = torch.arange(len(inverse), device=tot_counts.device)[tot_counts]
        
        out = {'x': x, 'index': index}
        if return_inverse:
            out['inverse'] = inverse
        if return_counts:
            out['counts'] = counts

        # the following code doesn't work right now on MPS due to MPS determinism bug
#         ret = torch.unique_consecutive(x, dim=0, return_inverse=True, return_counts=return_counts)

#         x, inverse = ret[0], ret[1]
#         args = (len(inverse)-1, -1, -1) if first_index else (len(inverse),)
#         with use_deterministic_algorithms() if first_index else contextlib.nullcontext():
#             # scatter_ is non-deterministic by default and would result in a random index rather than the first index
#             index = inverse.new_empty(len(x)).scatter_(
#                 0,
#                 inverse.flip(0) if first_index else inverse,
#                 torch.arange(*args, dtype=inverse.dtype, device=inverse.device),
#             )
        
#         # gather results into a dictionary
#         out = {'x': x, 'index': index}
#         if return_inverse:
#             out['inverse'] = inverse
#         if return_counts:
#             out['counts'] = ret[2]

    else:
        ret = torch.unique_consecutive(x, dim=0, return_inverse=return_inverse, return_counts=return_counts)

        # gather results into a dictionary
        ret = list(ret) if isinstance(ret, tuple) else [ret]
        out = {'x': ret.pop(0)}
        if return_inverse:
            out['inverse'] = ret.pop(0)
        if return_counts:
            out['counts'] = ret.pop(0)
            
    # correct for the fact that we reshaped and sorted before computing unqiue
    out['x'] = out['x'].reshape(-1, *shape[1:]).movedim(0, dim)
    if return_index or return_inverse:
        if return_index:
            out['index'] = sort_idx[out['index']]
        if return_inverse:
            sort_idx_inv = inv_perm(sort_idx)
            out['inverse'] = out['inverse'][sort_idx_inv]
    
    if len(out) == 1:
        return out['x']
    return tuple(out.values())

def unique(x, dim=None, sorted=True, return_index=False, return_inverse=False, return_counts=False, equal_nan=False, first_index=True):
    """
    Note:
     - When sorted=False, there is no guarantee on what the result order will be.
     - The result of this function when sorted=True, return_index=False is slightly different from numpy
     with return_index=False since numpy does not use stable sort when return_index=False, only when return_index=True.
     - If return_index=True and first_index=True, the returned index is the first index of the unique element. Otherwise,
        the returned index can correspond to any index of the unique element, and the behavior is non-deterministic.
    """
    
    if equal_nan:
        raise NotImplementedError("pytorch currently does not support equal_nan=True")
    
    # unique_dim currently not implemented for MPS, so do _unique_sorted instead
    # which uses unique_consecutive (which has MPS implementation) instead of unique_dim.
    # the reason there is no MPS unqiue_dim support right now is that there is currently 
    # no native MPS support for sorting with custom compare and equal functions, so one 
    # has to write a custom MPS Kernel which means it might take a long while before this gets implemented.
    if sorted or x.device.type == 'mps':
        return _unique_sorted(x, dim=dim, return_index=return_index, return_inverse=return_inverse, return_counts=return_counts)
    
    if dim is None:
        x = x.reshape(-1)
        dim = 0
    
    # reshape to a 2D tensor where we compute unique rows
    x = x.movedim(dim, 0)
    shape = x.shape
    x = x.reshape(shape[0], -1)
    
    # separate rows with nans from rows without nans and only compute unique on rows without nans.
    # This avoids torch.unique bug when dim is not None and input has nan.
    isnan = x.isnan().any(dim=1)
    if not isnan.any():
        x_not_isnan, x_isnan = x, torch.empty((0, x.shape[1]), dtype=x.dtype, device=x.device) # slighty optimization to prevent large copy
    else:
        x_not_isnan, x_isnan = x[~isnan], x[isnan]
    N_not_isnan = len(x_not_isnan)

    if return_index:
        # # code copied from https://github.com/pytorch/pytorch/issues/36748#issuecomment-1474368922
        # x_not_isnan, inverse, counts = torch.unique(x_not_isnan, dim=0, return_inverse=True, return_counts=True)
        # inv_sort_idx = inverse.argsort(stable=True)
        # tot_counts = torch.cat((counts.new_zeros(1), counts.cumsum(dim=0)))[:-1]
        # index = inv_sort_idx[tot_counts]

        # out = {'x': x_not_isnan, 'index': index}
        # if return_inverse:
        #     out['inverse'] = inverse
        # if return_counts:
        #     out['counts'] = counts

        ret = torch.unique(x_not_isnan, dim=0, return_inverse=True, return_counts=return_counts)

        x_not_isnan, inverse = ret[0], ret[1]
        args = (len(inverse)-1, -1, -1) if first_index else (len(inverse),)
        with use_deterministic_algorithms() if first_index else contextlib.nullcontext():
            # scatter_ is non-deterministic by default and would result in a random index rather than the first index
            index = inverse.new_empty(len(x_not_isnan)).scatter_(
                0,
                inverse.flip(0) if first_index else inverse,
                torch.arange(*args, dtype=inverse.dtype, device=inverse.device),
            )

        # gather results into a dictionary
        out = {'x': x_not_isnan, 'index': index}
        if return_inverse:
            out['inverse'] = inverse
        if return_counts:
            out['counts'] = ret[2]

    else:
        ret = torch.unique(x_not_isnan, dim=0, return_inverse=return_inverse, return_counts=return_counts)
    
        # gather results into a dictionary
        ret = list(ret) if isinstance(ret, tuple) else [ret]
        out = {'x': ret.pop(0)}
        if return_inverse:
            out['inverse'] = ret.pop(0)
        if return_counts:
            out['counts'] = ret.pop(0)
        
    # append nans to the end of the unique tensor and handle index, inverse, and counts accordingly
    N_unique_not_isnan = len(out['x'])
    out['x'] = torch.cat([out['x'], x_isnan])
    if return_index:
        out['index'] = torch.cat([out['index'], torch.arange(len(x_isnan), device=x.device) + N_not_isnan])
    if return_inverse:
        out['inverse'] = torch.cat([out['inverse'], torch.arange(len(x_isnan), device=x.device) + N_unique_not_isnan])
    if return_counts:
        out['counts'] = torch.cat([out['counts'], out['counts'].new_ones(len(x_isnan))])
    
    # correct for the fact that we reshaped and modified element order before computing unqiue
    out['x'] = out['x'].reshape(-1, *shape[1:]).movedim(0, dim)
    if return_index or return_inverse:
        sort_idx = torch.cat(((~isnan).nonzero(), isnan.nonzero())).squeeze()
        if return_index:
            out['index'] = sort_idx[out['index']]
        if return_inverse:
            sort_idx_inv = inv_perm(sort_idx)
            out['inverse'] = out['inverse'][sort_idx_inv]
    
    if len(out) == 1:
        return out['x']
    return tuple(out.values())

def meshgrid(*tensors, indexing='ij', ndims=None):
    """
    The most general version of torch.meshgrid. Meshes together tensors of shapes
    (n_1_1,...,n_1_{ndims_1},*_1), (n_2_1,...,n_2_{ndims_2},*_2), ..., (n_P_1,...,n_P_{ndims_P},*_P).
    indexing must be either 'ij' or 'xy'. Defaults to 'ij' like pytorch but unlike numpy.
    If ndims is None, meshes over all dimensions. ndims can be an int or an Iterable.
    Negative ndim has the same semantic meaning as slicing with a negative index.
    
    If indexing == 'ij', returns tensors of shapes 
    (n_1_1,...,n_1_{ndims_1},n_2_1,...,n_2_{ndims_2},...,n_P_1,...,n_P_{ndims_P},*_1),
    (n_1_1,...,n_1_{ndims_1},n_2_1,...,n_2_{ndims_2},...,n_P_1,...,n_P_{ndims_P},*_2),
    ...
    (n_1_1,...,n_1_{ndims_1},n_2_1,...,n_2_{ndims_2},...,n_P_1,...,n_P_{ndims_P},*_P)
    
    Otherwise, returns tensors of shapes
    (n_2_1,...,n_2_{ndims_2},n_1_1,...,n_1_{ndims_1},...,n_P_1,...,n_P_{ndims_P},*_1),
    (n_2_1,...,n_2_{ndims_2},n_1_1,...,n_1_{ndims_1},...,n_P_1,...,n_P_{ndims_P},*_2),
    ...
    (n_2_1,...,n_2_{ndims_2},n_1_1,...,n_1_{ndims_1},...,n_P_1,...,n_P_{ndims_P},*_P)
    
    IMPORTANT: Data is NOT copied just like pytorch, but unlike numpy which copies by default.
    """
    if not indexing in {'ij', 'xy'}:
        raise ValueError(f"indexing must 'ij' or 'xy', but got {indexing}.")
    
    if not isinstance(ndims, collections.abc.Iterable):
        ndims = [ndims] * len(tensors)
    elif iter(ndims) is ndims:
        ndims = list(ndims)
        
    if not all(isinstance(ndim, int) or ndim is None for ndim in ndims):
        raise TypeError(f"ndim must be None or an int, but got {ndims}.")

    if len(ndims) != len(tensors):
        raise ValueError(
            f"""ndims must have same number of elements as input tensors,
            but got {len(ndims)=} and {len(tensors)=}."""
        )
        
    if not all(
        abs(ndim) <= tensor.ndim
        for tensor, ndim in zip(tensors, ndims) if isinstance(ndim, int)
    ):
        raise ValueError(
            f"""abs(ndim) cannot be greater than the corresponding tensor.ndim, but
            {ndims=} while tensor ndims={[tensor.ndim for tensor in tensors]}."""
        )
    
    cumndims = list(itertools.accumulate((
        tensor.ndim if ndim is None else tensor.ndim + ndim if ndim < 0 else ndim
        for tensor, ndim in zip(tensors, ndims)
    )))
    pre_cumndims = [0] + cumndims[:-1]
    post_cumndims = (cumndims[-1] - cumndim for cumndim in cumndims)
    pre_shapes, post_shapes = zip(*(
        (tensor.shape[:ndim], () if ndim is None else tensor.shape[ndim:])
        for tensor, ndim in zip(tensors, ndims)
    ))
    shapes = (
        (1,) * pre_cumndim + pre_shape + (1,) * post_cumndim + post_shape
        for pre_shape, post_shape, pre_cumndim, post_cumndim
        in zip(pre_shapes, post_shapes, pre_cumndims, post_cumndims)
    )
    shared_shape = tuple(itertools.chain(*pre_shapes))
    tensors = (
        tensor.reshape(shape).broadcast_to(shared_shape + post_shape)
        for tensor, shape, post_shape in zip(tensors, shapes, post_shapes)
    )
    
    if indexing == 'ij':
        return list(tensors)
        
    return [
        tensor.movedim(
            tuple(range(cumndims[0], cumndims[1])),
            tuple(range(cumndims[1] - cumndims[0]))
        )
        for tensor in tensors
    ]

@contextlib.contextmanager
def use_deterministic_algorithms():
    """
    Context manager to use deterministic algorithms.
    """
    is_deterministic = torch.are_deterministic_algorithms_enabled()
    try:
        torch.use_deterministic_algorithms(True)
        yield
    finally:
        torch.use_deterministic_algorithms(is_deterministic)

##########################################
### Implemented but untested functions ###
##########################################

# import numpy as np

# def ravel_multi_index(multi_index, dims):
#     """
#     Similar to np.ravel_multi_index
#     """
#     multi_index = torch.stack(multi_index) if not isinstance(multi_index, torch.Tensor) else multi_index
#     dims = torch.as_tensor(dims, device=multi_index.device)
    
#     if len(multi_index) != len(dims):
#         raise ValueError(f"multi_index and dims must have same length, but {len(multi_index)=} and {len(dims)=}.")
    
#     if torch.is_floating_point(multi_index):
#         raise TypeError(f"multi_index must be integer dtype, but {multi_index.dtype=}.")
        
#     if (multi_index.min(dim=1).values < 0).any():
#         raise ValueError(f"multi_index must be non-negative, but {multi_index.min(dim=1).values=}.")
        
#     if (multi_index.max(dim=1).values >= dims).any():
#         raise ValueError(f"multi_index must be less than dims along each dimension, but {multi_index.max(dim=1).values=} and {dims=}.")
        
#     multipliers = np.cumprod((dims[1:].tolist() + [1])[::-1])[::-1]
#     return torch.stack([index * multiplier for index, multiplier in zip(multi_index, multipliers)], dim=0).sum(dim=0)

# def unravel_index(indices, shape, *, as_tuple=True):
#     r"""
#     Modified from https://github.com/pytorch/pytorch/pull/66687/files
    
#     Converts a `Tensor` of flat indices into a `Tensor` of coordinates for the given target shape.
#     Args:
#         indices: An integral `Tensor` containing flattened indices of a `Tensor` of dimension `shape`.
#         shape: The shape (can be an `int`, a `Sequence` or a `Tensor`) of the `Tensor` for which
#                the flattened `indices` are unraveled.
#     Keyword Args:
#         as_tuple: A boolean value, which if `True` will return the result as tuple of Tensors,
#                   else a `Tensor` will be returned. Default: `True`
#     Returns:
#         unraveled coordinates from the given `indices` and `shape`. See description of `as_tuple` for
#         returning a `tuple`.
#     .. note:: The default behaviour of this function is analogous to
#               `numpy.unravel_index <https://numpy.org/doc/stable/reference/generated/numpy.unravel_index.html>`_.
#     Example::
#         >>> indices = torch.tensor([22, 41, 37])
#         >>> shape = (7, 6)
#         >>> torch.unravel_index(indices, shape)
#         (tensor([3, 6, 6]), tensor([4, 5, 1]))
#         >>> torch.unravel_index(indices, shape, as_tuple=False)
#         tensor([[3, 4],
#                 [6, 5],
#                 [6, 1]])
#         >>> indices = torch.tensor([3, 10, 12])
#         >>> shape_ = (4, 2, 3)
#         >>> torch.unravel_index(indices, shape_)
#         (tensor([0, 1, 2]), tensor([1, 1, 0]), tensor([0, 1, 0]))
#         >>> torch.unravel_index(indices, shape_, as_tuple=False)
#         tensor([[0, 1, 0],
#                 [1, 1, 1],
#                 [2, 0, 0]])
#     """
#     def _helper_type_check(inp, name):
#         # `indices` is expected to be a tensor, while `shape` can be a sequence/int/tensor
#         if name == "shape" and isinstance(inp, collections.abc.Sequence):
#             for dim in inp:
#                 if not isinstance(dim, int):
#                     raise TypeError("Expected shape to have only integral elements.")
#                 if dim < 0:
#                     raise ValueError("Negative values in shape are not allowed.")
#         elif name == "shape" and isinstance(inp, int):
#             if inp < 0:
#                 raise ValueError("Negative values in shape are not allowed.")
#         elif isinstance(inp, torch.Tensor):
#             if torch.is_floating_point(inp):
#                 raise TypeError(f"Expected {name} to be an integral tensor, but found dtype: {inp.dtype}")
#             if torch.any(inp < 0):
#                 raise ValueError(f"Negative values in {name} are not allowed.")
#         else:
#             allowed_types = "Sequence/Scalar (int)/Tensor" if name == "shape" else "Tensor"
#             msg = f"{name} should either be a {allowed_types}, but found {type(inp)}"
#             raise TypeError(msg)

#     _helper_type_check(indices, "indices")
#     _helper_type_check(shape, "shape")

#     # Convert to a tensor, with the same properties as that of indices
#     if isinstance(shape, collections.abc.Sequence):
#         shape_tensor = indices.new_tensor(shape)
#     elif isinstance(shape, int) or (isinstance(shape, Tensor) and shape.ndim == 0):
#         shape_tensor = indices.new_tensor((shape,))
#     else:
#         shape_tensor = shape

#     # By this time, shape tensor will have dim = 1 if it was passed as scalar (see if-elif above)
#     assert shape_tensor.ndim == 1, "Expected dimension of shape tensor to be <= 1, "
#     f"but got the tensor with dim: {shape_tensor.ndim}."

#     # In case no indices passed, return an empty tensor with number of elements = shape.numel()
#     if indices.numel() == 0:
#         # If both indices.numel() == 0 and shape.numel() == 0, short-circuit to return itself
#         shape_numel = shape_tensor.numel()
#         if shape_numel == 0:
#             raise ValueError("Got indices and shape as empty tensors, expected non-empty tensors.")
#         else:
#             output = [indices.new_tensor([]) for _ in range(shape_numel)]
#             return tuple(output) if as_tuple else torch.stack(output, dim=1)

#     if torch.max(indices) >= torch.prod(shape_tensor):
#         raise ValueError("Target shape should cover all source indices.")

#     coefs = shape_tensor[1:].flipud().cumprod(dim=0).flipud()
#     coefs = torch.cat((coefs, coefs.new_tensor((1,))), dim=0)
#     coords = torch.div(indices[..., None], coefs, rounding_mode='trunc') % shape_tensor

#     if as_tuple:
#         return tuple(coords[..., i] for i in range(coords.size(-1)))
#     return coords