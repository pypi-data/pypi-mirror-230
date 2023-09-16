import builtins
from operator import index
from collections import namedtuple

import numpy as np
from numpy.testing import suppress_warnings
from scipy import stats as spstats
import statsmodels.api as sm

from ..np import stats as npstats

BinnedStatisticddResult = namedtuple('BinnedStatisticddResult',
                                     ('statistic', 'bin_edges',
                                      'binnumber'))
LinregressResult = namedtuple('LinregressResult', ('slope', 'intercept', 'rvalue', 'pvalue', 'stderr', 'intercept_stderr'))

def linregress(x, y, yerr=None, alternative='two-sided'):
    if alternative != 'two-sided':
        raise NotImplementedError('currently only allow alternative == "two-sided".')
        
    if yerr is not None:
        weights = 1/yerr**2
    else:
        weights = 1.0
        
    x = np.asarray(x)
    y = np.asarray(y)
    weights = np.asarray(weights)
        
    model = sm.WLS(y, sm.add_constant(x), weights=weights)
    res = model.fit()
    res = LinregressResult(
        slope=res.params[1],
        intercept=res.params[0],
        rvalue=res.rsquared**0.5,
        pvalue=res.pvalues[1],
        stderr=res.bse[1],
        intercept_stderr=res.bse[0],
    )
    return res

def _bincount(x, weights):
    if np.iscomplexobj(weights):
        a = np.bincount(x, np.real(weights))
        b = np.bincount(x, np.imag(weights))
        z = a + b*1j

    else:
        z = np.bincount(x, weights)
    return z

def _bin_edges(sample, bins=None, range=None):
    """ Create edge arrays
    """
    Dlen, Ndim = sample.shape

    nbin = np.empty(Ndim, int)    # Number of bins in each dimension
    edges = Ndim * [None]         # Bin edges for each dim (will be 2D array)
    dedges = Ndim * [None]        # Spacing between edges (will be 2D array)

    # Select range for each dimension
    # Used only if number of bins is given.
    if range is None:
        smin = np.atleast_1d(np.array(np.nanmin(sample, axis=0), float))
        smax = np.atleast_1d(np.array(np.nanmax(sample, axis=0), float))
    else:
        if len(range) != Ndim:
            raise ValueError(
                f"range given for {len(range)} dimensions; {Ndim} required")
        smin = np.empty(Ndim)
        smax = np.empty(Ndim)
        for i in builtins.range(Ndim):
            if range[i][1] < range[i][0]:
                raise ValueError(
                    "In {}range, start must be <= stop".format(
                        f"dimension {i + 1} of " if Ndim > 1 else ""))
            smin[i], smax[i] = range[i]

    # Make sure the bins have a finite width.
    for i in builtins.range(len(smin)):
        if smin[i] == smax[i]:
            smin[i] = smin[i] - .5
            smax[i] = smax[i] + .5

    # Preserve sample floating point precision in bin edges
    edges_dtype = (sample.dtype if np.issubdtype(sample.dtype, np.floating)
                   else float)

    # Create edge arrays
    for i in builtins.range(Ndim):
        if np.isscalar(bins[i]):
            nbin[i] = bins[i] + 2  # +2 for outlier bins
            edges[i] = np.linspace(smin[i], smax[i], nbin[i] - 1,
                                   dtype=edges_dtype)
        else:
            edges[i] = np.asarray(bins[i], edges_dtype)
            nbin[i] = len(edges[i]) + 1  # +1 for outlier bins
        dedges[i] = np.diff(edges[i])

    nbin = np.asarray(nbin)

    return nbin, edges, dedges


def _bin_numbers(sample, nbin, edges, dedges, expand_binnumbers=False):
    """Compute the bin number each sample falls into, in each dimension
    """
    Dlen, Ndim = sample.shape

    sampBin = [
        np.digitize(sample[:, i], edges[i])
        for i in range(Ndim)
    ]

    # Using `digitize`, values that fall on an edge are put in the right bin.
    # For the rightmost bin, we want values equal to the right
    # edge to be counted in the last bin, and not as an outlier.
    for i in range(Ndim):
        # Find the rounding precision
        dedges_min = dedges[i].min()
        if dedges_min == 0:
            raise ValueError('The smallest edge difference is numerically 0.')
        decimal = int(-np.log10(dedges_min)) + 6
        # Find which points are on the rightmost edge.
        on_edge = np.where((sample[:, i] >= edges[i][-1]) &
                           (np.around(sample[:, i], decimal) ==
                            np.around(edges[i][-1], decimal)))[0]
        # Shift these points one bin to the left.
        sampBin[i][on_edge] -= 1

    if expand_binnumbers:
        binnumbers = np.stack(sampBin)
    else:
        # Compute the sample indices in the flattened statistic matrix.
        binnumbers = np.ravel_multi_index(sampBin, nbin)

    return binnumbers


def _create_binned_data(bin_numbers, unique_bin_numbers, values, vv):
    """ Create hashmap of bin ids to values in bins
    key: bin number
    value: list of binned data
    """
    bin_map = dict()
    for i in unique_bin_numbers:
        bin_map[i] = []
    for i in builtins.range(len(bin_numbers)):
        bin_map[bin_numbers[i]].append(values[vv, i])
    return bin_map

def _calc_binned_statistic(Vdim, bin_numbers, result, values, stat_func, values_err=None):
    unique_bin_numbers = np.unique(bin_numbers)
    for vv in builtins.range(Vdim):
        bin_map = _create_binned_data(bin_numbers, unique_bin_numbers,
                                      values, vv)
        if values_err is not None:
            err_bin_map = _create_binned_data(bin_numbers, unique_bin_numbers,
                                      values_err, vv)
        for i in unique_bin_numbers:
            stat = stat_func(np.array(bin_map[i])) if values_err is None else stat_func(np.array(bin_map[i]), np.array(err_bin_map[i]))
            if np.iscomplexobj(stat) and not np.iscomplexobj(result):
                raise ValueError("The statistic function returns complex ")
            result[vv, i] = stat

def binned_statistic_dd(sample, values, values_err=None, statistic='mean',
                        bins=10, range=None, expand_binnumbers=False,
                        binned_statistic_result=None, nan_policy='raise'):
    if nan_policy not in ['raise', 'omit']:
        raise ValueError(f"nan_policy must be 'raise' or 'omit', but {nan_policy=}.")
    
    known_stats = ['mean', 'median', 'count', 'sum', 'std', 'min', 'max']
    if not callable(statistic) and statistic not in known_stats:
        raise ValueError('invalid statistic %r' % (statistic,))

    try:
        bins = index(bins)
    except TypeError:
        # bins is not an integer
        pass
    # If bins was an integer-like object, now it is an actual Python int.

    # NOTE: for _bin_edges(), see e.g. gh-11365
    if nan_policy == 'raise' and not np.isfinite(sample).all():
        raise ValueError('%r contains non-finite values.' % (sample,))

    # `Ndim` is the number of dimensions (e.g. `2` for `binned_statistic_2d`)
    # `Dlen` is the length of elements along each dimension.
    # This code is based on np.histogramdd
    try:
        # `sample` is an ND-array.
        Dlen, Ndim = sample.shape
    except (AttributeError, ValueError):
        # `sample` is a sequence of 1D arrays.
        sample = np.atleast_2d(sample).T
        Dlen, Ndim = sample.shape

    # Store initial shape of `values` to preserve it in the output
    values = np.asarray(values)
    if values_err is not None:
        values_err = np.asarray(values_err)
        try:
            values, values_err = np.broadcast_arrays(values, values_err)
        except ValueError as err:
            raise AttributeError(f'shape of values must match shape of values_err, but got {values.shape=} and {values_err.shape=}') from err
    input_shape = list(values.shape)
    # Make sure that `values` is 2D to iterate over rows
    values = np.atleast_2d(values)
    if values_err is not None:
        values_err = np.atleast_2d(values_err)
    Vdim, Vlen = values.shape

    # Make sure `values` match `sample`
    if statistic != 'count' and Vlen != Dlen:
        raise AttributeError('The number of `values` elements must match the '
                             f'length of each `sample` dimension, but got {sample.shape=} and {values.shape=}')

    try:
        M = len(bins)
        if M != Ndim:
            raise AttributeError('The dimension of bins must be equal '
                                 'to the dimension of the sample x.')
    except TypeError:
        bins = Ndim * [bins]

    if binned_statistic_result is None:
        nbin, edges, dedges = _bin_edges(sample, bins, range)
        binnumbers = _bin_numbers(sample, nbin, edges, dedges)
    else:
        edges = binned_statistic_result.bin_edges
        nbin = np.array([len(edges[i]) + 1 for i in builtins.range(Ndim)])
        # +1 for outlier bins
        dedges = [np.diff(edges[i]) for i in builtins.range(Ndim)]
        binnumbers = binned_statistic_result.binnumber

    # Avoid overflow with double precision. Complex `values` -> `complex128`.
    if values_err is None:
        result_type = np.result_type(values, np.float64)
    else:
        result_type = np.result_type(values, values_err, np.float64)
    
    result = np.empty([Vdim, nbin.prod()], dtype=result_type)

    if statistic in {'mean', np.mean}:
        result.fill(np.nan)
        flatcount = _bincount(binnumbers, None)
        a = flatcount.nonzero()
        for vv in builtins.range(Vdim):
            flatsum = _bincount(binnumbers, values[vv])
            result[vv, a] = flatsum[a] / flatcount[a]
    elif statistic in {'std', np.std}:
        result.fill(np.nan)
        flatcount = _bincount(binnumbers, None)
        a = flatcount.nonzero()
        for vv in builtins.range(Vdim):
            flatsum = _bincount(binnumbers, values[vv])
            delta = values[vv] - flatsum[binnumbers] / flatcount[binnumbers]
            std = np.sqrt(
                _bincount(binnumbers, delta*np.conj(delta))[a] / flatcount[a]
            )
            result[vv, a] = std
        result = np.real(result)
    elif statistic == 'count':
        result = np.empty([Vdim, nbin.prod()], dtype=np.float64)
        result.fill(0)
        flatcount = _bincount(binnumbers, None)
        a = np.arange(len(flatcount))
        result[:, a] = flatcount[np.newaxis, :]
    elif statistic in {'sum', np.sum}:
        result.fill(0)
        for vv in builtins.range(Vdim):
            flatsum = _bincount(binnumbers, values[vv])
            a = np.arange(len(flatsum))
            result[vv, a] = flatsum
    elif statistic in {'median', np.median}:
        result.fill(np.nan)
        for vv in builtins.range(Vdim):
            i = np.lexsort((values[vv], binnumbers))
            _, j, counts = np.unique(binnumbers[i],
                                     return_index=True, return_counts=True)
            mid = j + (counts - 1) / 2
            mid_a = values[vv, i][np.floor(mid).astype(int)]
            mid_b = values[vv, i][np.ceil(mid).astype(int)]
            medians = (mid_a + mid_b) / 2
            result[vv, binnumbers[i][j]] = medians
    elif statistic in {'min', np.min}:
        result.fill(np.nan)
        for vv in builtins.range(Vdim):
            i = np.argsort(values[vv])[::-1]  # Reversed so the min is last
            result[vv, binnumbers[i]] = values[vv, i]
    elif statistic in {'max', np.max}:
        result.fill(np.nan)
        for vv in builtins.range(Vdim):
            i = np.argsort(values[vv])
            result[vv, binnumbers[i]] = values[vv, i]
    elif callable(statistic):
        with np.errstate(invalid='ignore'), suppress_warnings() as sup:
            sup.filter(RuntimeWarning)
            try:
                null = statistic([])
            except Exception:
                null = np.nan
        if np.iscomplexobj(null):
            result = result.astype(np.complex128)
        result.fill(null)
        try:
            _calc_binned_statistic(
                Vdim, binnumbers, result, values, statistic, values_err=values_err
            )
        except ValueError:
            result = result.astype(np.complex128)
            _calc_binned_statistic(
                Vdim, binnumbers, result, values, statistic, values_err=values_err
            )

    # Shape into a proper matrix
    result = result.reshape(np.append(Vdim, nbin))

    # Remove outliers (indices 0 and -1 for each bin-dimension).
    core = tuple([slice(None)] + Ndim * [slice(1, -1)])
    result = result[core]

    # Unravel binnumbers into an ndarray, each row the bins for each dimension
    if expand_binnumbers and Ndim > 1:
        binnumbers = np.asarray(np.unravel_index(binnumbers, nbin))

    if np.any(result.shape[1:] != nbin - 2):
        raise RuntimeError('Internal Shape Error')

    # Reshape to have output (`result`) match input (`values`) shape
    result = result.reshape(input_shape[:-1] + list(nbin-2))

    return BinnedStatisticddResult(result, edges, binnumbers)


def bin_dd(sample, bins=10, range=None, expand_binnumbers=True, nan_policy='raise'):
    """
    Bins N-dimensional data. Arguments have the same meaning as in scipy.stats.binned_statistic_dd,
    except that here expand_binnumbers=True by default, and that if expand_binnumbers=True and N = 1,
    then binnumbers is 2D instead of 1D as in scipy.stats.binned_statistic_dd.
    nan_policy can be 'raise' or 'omit'. 
    If nan_policy='raise', then ValueError is raised if sample contains any NaNs (this is slightly different
    from the default behavior of scipy.stats.binned_statistic_dd).
    If nan_policy='omit', NaNs are sorted into the rightmost bin.
    """
    
    if nan_policy not in ['raise', 'omit']:
        raise ValueError(f"nan_policy must be 'raise' or 'omit', but {nan_policy=}.")
    
    try:
        bins = index(bins)
    except TypeError:
        # bins is not an integer
        pass
    # If bins was an integer-like object, now it is an actual Python int.

    # NOTE: for _bin_edges(), see e.g. gh-11365
    if nan_policy == 'raise' and not np.isfinite(sample).all():
        raise ValueError('%r contains non-finite values.' % (sample,))

    # `Ndim` is the number of dimensions (e.g. `2` for `binned_statistic_2d`)
    # `Dlen` is the length of elements along each dimension.
    # This code is based on np.histogramdd
    try:
        # `sample` is an ND-array.
        Dlen, Ndim = sample.shape
    except (AttributeError, ValueError):
        # `sample` is a sequence of 1D arrays.
        sample = np.atleast_2d(sample).T
        Dlen, Ndim = sample.shape
        
    try:
        M = len(bins)
        if M != Ndim:
            raise AttributeError('The dimension of bins must be equal '
                                 'to the dimension of the sample x.')
    except TypeError:
        bins = Ndim * [bins]
        
    nbin, edges, dedges = _bin_edges(sample, bins, range)
    binnumbers = _bin_numbers(sample, nbin, edges, dedges, expand_binnumbers=expand_binnumbers)
        
    centers = [np.array([np.nan] + list(0.5*(e[:-1]+e[1:])) + [np.nan]) for e in edges]
    return binnumbers, centers, edges

def bin(sample, bins=10, range=None, nan_policy='raise'):
    try:
        N = len(bins)
    except TypeError:
        N = 1

    if N != 1:
        bins = [np.asarray(bins, float)]

    if range is not None:
        if len(range) == 2:
            range = [range]
            
    bin_nums, centers, edges = bin_dd(sample, bins=bins, range=range, nan_policy=nan_policy)
    return bin_nums[0], centers[0], edges[0]

def binned_mean_dd(x, y, yerr=None, weighted=False, nanstats=True, **kwargs):
    nan = 'nan' if nanstats else ''
    weighted = 'weighted' if weighted else ''
    
    if yerr is not None:
        statistics = {
            'y': lambda y, yerr: getattr(npstats, f'{nan}{weighted}meanerr')(y, yerr)[0],
            'yerr': lambda y, yerr: getattr(npstats, f'{nan}{weighted}meanerr')(y, yerr)[1]
        }
    else:
        if weighted:
            raise ValueError("weighted is True, but yerr is not provided")
            
        statistics = {
            'y': lambda y: getattr(npstats, f'{nan}mean')(y),
            'yerr': lambda y: getattr(npstats, f'{nan}sem')(y),
        }
    
    result = {}
    
    out = binned_statistic_dd(x, y, values_err=yerr, statistic=statistics['y'], **kwargs)
    
    bin_edges = out.bin_edges
    bin_centers = [0.5*(edges[:-1] + edges[1:]) for edges in bin_edges]
    grid = np.stack(np.meshgrid(*bin_centers, indexing='ij'), axis=-1)
    result['x'] = grid
    result['y'] = out.statistic
    
    out = binned_statistic_dd(x, y, values_err=yerr, statistic=statistics['yerr'], binned_statistic_result=out, **kwargs)
    result['yerr'] = out.statistic
    
    return result

def binned_mean(x, y, yerr=None, bins=10, range=None, **kwargs):
    try:
        N = len(bins)
    except TypeError:
        N = 1

    if N != 1:
        bins = [np.asarray(bins, float)]

    if range is not None:
        if len(range) == 2:
            range = [range]

    result = binned_mean_dd(
        [x], y, yerr=yerr, bins=bins, range=range, **kwargs)
    
    result['x'] = result['x'].squeeze()
    
    return result