import functools
import logging
from datetime import datetime

import numpy as np
import numpy.ma as ma
import torch
import pandas as pd

from .sp import stats

logger = logging.getLogger(__name__)

def _formatter(x, float_format=None, datetime_format=None, verbose=False):
    if float_format is None:
        float_format = '{:.4f}'.format
    if datetime_format is None:
        datetime_format = '{:%Y-%m-%d %H:%M:%S}'.format
        
    if isinstance(x, np.ndarray):
        if x.ndim == 0:
            if ma.is_masked(x):
                return "NA"
            elif isinstance(x, np.inexact):
                return float_format(x)
            else:
                return str(x)
        if verbose:
            return f"np.ndarray {x.shape} ({x.dtype})"
        return f"{x.shape}"
    if isinstance(x, torch.Tensor):
        if x.ndim == 0:
            if x.is_floating_point():
                return float_format(x.item())
            else:
                return str(x.item())
        if verbose:
            return f"torch.Tensor {tuple(x.shape)} ({x.dtype})"
        return f"{tuple(x.shape)}"
    if isinstance(x, tuple):
        if verbose:
            return f"tuple ({len(x)}) {tuple([type(e).__name__ for e in x])}"
        return f"tuple ({len(x)})"
    if isinstance(x, list):
        if verbose:
            return f"list ({len(x)}) {[type(e).__name__ for e in x]}"
        return f"list ({len(x)})"
    if isinstance(x, dict):
        if verbose:
            d = {k: type(v).__name__ for k, v in x.items()}
            return f"dict ({len(x)}) {d}"
        return f"dict ({len(x)})"
    if isinstance(x, np.inexact):
        return float_format(x)
    if isinstance(x, datetime):
        return datetime_format(x)
    return str(x)

def display(df, float_format=None, datetime_format=None, verbose=False, **kwargs):
    default_kwargs = {
        'max_rows': 6,
        'show_dimensions': True,
        'formatters': {k: functools.partial(_formatter, float_format=float_format, datetime_format=datetime_format, verbose=verbose) for k in df.columns},
    }
    default_kwargs.update(kwargs)

    try:
        get_ipython
        from IPython.display import display as ipy_display
        from IPython.core.display import HTML
    except:
        raise RuntimeError("display only works in jupyter notebook")
        
    ipy_display(HTML(df.to_html(**default_kwargs)))
    
def digitize(x, column=None, colname=None, copy=True, new_cols=True, **kwargs):
    if isinstance(x, pd.Series):
        if column is not None:
            logger.warning("Attemping to digitize pd.Series with non-None column argument. column argument is ignored.")
        if colname is None:
            colname = 'x'
        column = colname
        x = pd.DataFrame({colname: x})
            
    elif isinstance(x, pd.DataFrame):
        if colname is not None:
            logger.warning("Attemping to digitize pd.DataFrame with non-None colname argument. colname argument is ignored.")
        if len(x.columns) == 1:
            column = x.columns.values[0] if column is None else column
        if len(x.columns) > 1 and column is None:
            raise ValueError("column must be provided if number of columns in the provided dataframe is greater than 1.")
            
    else:
        raise TypeError(f"x must be pd.Series or pd.DataFrame, but {type(x)} provided.")
        
    if copy:
        x = x.copy() # not necessary if x was a pd.Series, but whatever
        
    if isinstance(column, str):
        sample = revert_dtypes(x[column]).to_numpy()
        bin_nums, centers, edges = stats.bin(sample, nan_policy='omit', **kwargs)
        if new_cols:
            x[f'{column}_bin_center'] = centers[bin_nums]
            x[f'{column}_bin_ledge'] = np.array([-np.inf] + list(edges))[bin_nums]
            x[f'{column}_bin_redge'] = np.array(list(edges) + [np.inf])[bin_nums]
        else:
            x[column] = centers[bin_nums]
    else:
        sample = np.array([revert_dtypes(x[c]).to_numpy() for c in column]).T # (N,D)
        bin_nums, centers, edges = stats.bin_dd(sample, nan_policy='omit', **kwargs)
        for b, c, e, col in zip(bin_nums, centers, edges, column):
            if new_cols:
                x[f'{col}_bin_center'] = c[b]
                x[f'{col}_bin_ledge'] = np.array([-np.inf] + list(e))[b]
                x[f'{col}_bin_redge'] = np.array(list(e) + [np.inf])[b]
            else:
                x[col] = c[b]
            
    if new_cols:
        return x
    return x, edges

def mean(df, *, by, y='y'):
    df = df.copy()
    yerr = f'{y}err'
    group = df.groupby(by)
    df = pd.DataFrame({
        y: group[y].mean(),
        yerr: group[y].sem(),
    }).reset_index()
    return df

def meanerr(df, *, by, y='y', yerr='yerr'):
    assert all([x not in ['y_', 'yvar'] for x in [y, yerr]])
    df = df.copy()
    df['y_'] = df[y] + df[yerr]*0
    df['yvar'] = df[y]*0 + df[yerr]**2
    group = df.groupby(by)
    df = pd.DataFrame({
        y: group['y_'].mean(),
        yerr: (group['yvar'].mean() + group['y_'].var())**0.5 / group['y_'].count()**0.5,
    }).reset_index()
    return df
    
def get_np_dtype(x):
    if not isinstance(x, pd.Series):
        raise TypeError(f'input must be pd.Series, but got {type(x)}')
    
    dtype = str(x.dtype)
    if 'Int' in dtype:
        if x.isnull().any():
            return 'float'
        return dtype.lower()
    elif 'Float' in dtype:
        return dtype.lower()
    elif 'boolean' in dtype:
        if x.isnull().any():
            return 'float'
        return 'bool'
    elif pd.api.types.is_numeric_dtype(dtype): # could be complex, for example
        return dtype
    else:
        return 'object'
    
def revert_dtypes(x):
    if isinstance(x, pd.Series):
        return x.astype(get_np_dtype(x))
    
    if isinstance(x, pd.DataFrame):
        dtypes = {col: get_np_dtype(x[col]) for col in x.columns}
        return x.astype(dtypes)
    
    raise TypeError(f'x must be pd.Series or pd.DataFrame, but got {type(x)}')

def to_tensor(x):
    is_list = False
    if isinstance(x, list):
        x = np.array(x)
        is_list = True
    if isinstance(x, np.ndarray):
        try:
            if x.dtype.kind in ['m', 'M', 'O', 'S', 'U', 'V']:
                return x.tolist() if is_list else x
            if x.dtype.kind == 'f':
                return torch.as_tensor(x, dtype=torch.float32)
            return torch.as_tensor(x)
        except Exception as err:
            raise RuntimeError(f'Error converting to tensor: {x.dtype=}, {x=}') from err
    return x

# update: df.join actually seems faster
# def cross_join(*dfs, maintain_dtypes=True):
#     """
#     Efficient cross/cartesian product of numeric dataframes. Should be faster than df.join()
#     If maintain_dtypes=True, will ensure that the resulting DataFrame has the same dtypes as the original DataFrames.
#     However, maintain_dtypes=True is very slow in general.
#     """
#     columns = [column for df in dfs for column in df.columns]
#     dtypes = {k: v for df in dfs for k, v in df.dtypes.items()}
#     dfs = meshgrid_dd(*(revert_dtypes(df).to_numpy() for df in dfs)) # reverting dtypes makes meshgrid faster if all columns are numeric
#     df = np.concatenate([df.reshape(-1,df.shape[-1]) for df in dfs], axis=-1)
#     df = pd.DataFrame(df, columns=columns)
#     if maintain_dtypes:
#         return df.astype(dtypes)
#     return df