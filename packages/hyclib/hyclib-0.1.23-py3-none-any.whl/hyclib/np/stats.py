import numpy as np
import numpy.ma as ma
from scipy import stats as spstats

__all__ = [
    'mean',
    'nanmean',
    'std',
    'nanstd',
    'var',
    'nanvar',
    'sem',
    'nansem',
    'count',
    'nancount',
    'cov',
    'nancov',
    'corrcoef',
    'nancorrcoef',
    'meanerr',
    'nanmeanerr',
    'weightedmeanerr',
    'nanweightedmeanerr',
    'bincount',
]

mean = np.mean
nanmean = np.nanmean

def std(x, ddof=1, **kwargs):
    return np.std(x, ddof=ddof, **kwargs)

def nanstd(x, ddof=1, **kwargs):
    return np.nanstd(x, ddof=ddof, **kwargs)

def var(x, ddof=1, **kwargs):
    return np.var(x, ddof=ddof, **kwargs)

def nanvar(x, ddof=1, **kwargs):
    return np.nanvar(x, ddof=ddof, **kwargs)
    
def sem(x, axis=None, ddof=1, **kwargs):
    return std(x, axis=axis, ddof=ddof, **kwargs) / count(x, axis=axis)**0.5
    # return spstats.sem(x, axis=axis, ddof=ddof)

def nansem(x, axis=None, ddof=1, **kwargs):
    return nanstd(x, axis=axis, ddof=ddof, **kwargs) / nancount(x, axis=axis)**0.5
    # return spstats.sem(x, axis=axis, ddof=ddof, nan_policy='omit')
    
def count(x, axis=None):
    return np.sum(np.ones(x.shape, dtype=int), axis=axis)

def nancount(x, axis=None):
    return np.sum(~np.isnan(x), axis=axis)
    
cov = np.cov # by default, np.cov uses Bessel correction, in contrast to the rest of its stats functions
    
def nancov(x, y=None, **kwargs):
    x = ma.masked_where(np.isnan(x), x)
    if y is not None:
        y = ma.masked_where(np.isnan(y), y)
    return ma.cov(x, y=y, **kwargs)
    
corrcoef = np.corrcoef

def nancorrcoef(x, y=None, **kwargs):
    x = ma.masked_where(np.isnan(x), x)
    if y is not None:
        y = ma.masked_where(np.isnan(y), y)
    return ma.corrcoef(x, y=y, **kwargs)

def meanerr(y, yerr, axis=None):
    y, yerr = np.array(y), np.array(yerr)
    
    assert y.shape == yerr.shape
    
    y = np.mean(y, axis=axis)
    yerr = np.sum(yerr**2, axis=axis)**0.5/count(yerr, axis=axis)
        
    return y, yerr

def nanmeanerr(y, yerr, axis=None):
    y, yerr = np.array(y), np.array(yerr)
    
    assert y.shape == yerr.shape
    
    nans = np.isnan(y) | np.isnan(yerr)
    y, yerr = y.copy(), yerr.copy()
    y[nans] = np.nan
    yerr[nans] = np.nan

    y = np.nanmean(y, axis=axis)
    yerr = np.nansum(yerr**2, axis=axis)**0.5/nancount(yerr, axis=axis)
        
    return y, yerr

def weightedmeanerr(y, yerr, axis=None):
    """
    Weighted mean and error of weighted mean
    
    Reference:
    Bevington and Robinson - Data Reduction and Error Analysis
    """
    y, yerr = np.array(y), np.array(yerr)
    
    assert y.shape == yerr.shape
    
    y = np.sum(y/yerr**2, axis=axis) / np.sum(1/yerr**2, axis=axis) # eq. 4.17 in reference
    yerr = 1/np.sum(1/yerr**2, axis=axis)**0.5 # eq 4.19 with square root
    
    return y, yerr
    
def nanweightedmeanerr(y, yerr, axis=None):
    """
    Weighted mean and error of weighted mean with np.nan values (either in mean or in error) ignored in the calculations.
    
    Reference:
    Bevington and Robinson - Data Reduction and Error Analysis
    """
    y, yerr = np.array(y), np.array(yerr)
    
    assert y.shape == yerr.shape
    
    nans = np.isnan(y) | np.isnan(yerr)
    y, yerr = y.copy(), yerr.copy()
    y[nans] = np.nan
    yerr[nans] = np.nan
    
    y = np.nansum(y/yerr**2, axis=axis) / np.nansum(1/yerr**2, axis=axis) # eq. 4.17 in reference
    yerr = 1/np.nansum(1/yerr**2, axis=axis)**0.5 # eq 4.19 with square root
    
    return y, yerr

def bincount(x, weights=None, minlength=0, nan_policy='propagate'):
    if nan_policy == 'propagate' or weights is None:
        return np.bincount(x, weights=weights, minlength=minlength)
    
    if nan_policy == 'omit':
        mask = np.isnan(weights)
        minlength = max(x.max() + 1, minlength)
        x = x[~mask]
        weights = weights[~mask]
        return np.bincount(x, weights=weights, minlength=minlength)
    
    raise ValueError(f"nan_policy must be 'propagate' or 'omit', but {nan_policy=}.")