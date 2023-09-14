# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import numpy as np

from cdtec.utils import compress


SERIES_MIN_NB_VALUES_FOR_CHANGE = 5


def _multi_change(single_change, arrays, dates,
                  threshold, nb_samples, no_data,
                  count=0):

    result = []

    change_before = np.full(single_change.shape, no_data)
    change_after = np.full(single_change.shape, no_data)

    for date in np.unique(single_change):
        if date != no_data:
            idx_before = dates < date
            idx_after = dates > date

            for idx, change in zip([idx_before, idx_after],
                                   [change_before, change_after]):
                _dates = dates[idx]
                series = arrays[idx, :, :]

                if _dates.size > SERIES_MIN_NB_VALUES_FOR_CHANGE:

                    _nb_samples = min(nb_samples, np.math.factorial(_dates.size))

                    chg = single_change_detection(series[:, single_change == date],
                                                  _dates, threshold, _nb_samples,
                                                  no_data=no_data)

                    if np.any(chg != no_data):
                        change[single_change == date] = chg
                        change_temp = np.full(single_change.shape, no_data)
                        change_temp[single_change == date] = chg
                        result.extend(_multi_change(change_temp, series,
                                                    _dates, threshold, nb_samples,
                                                    no_data, count + 1))

    if np.any(change_before != no_data):
        result.append(change_before)

    if np.any(change_after != no_data):
        result.append(change_after)

    return result


def change_intensity(arrays, dates, threshold, nb_samples, no_data):
    """ Compute intensity of single change (from date to date)

    Parameters
    ----------
    arrays
    dates
    threshold
    nb_samples
    no_data

    Returns
    -------

    """
    arrays = np.asarray(arrays)
    change = single_change_detection(arrays, dates, threshold, nb_samples, no_data)
    intensity = np.full(change.shape, no_data, dtype="float32")

    for date in np.unique(change):
        if date != no_data:
            try:
                diff = arrays[np.argwhere(dates == date).item() + 1, :, :] \
                       - arrays[dates == date, :, :]
                diff = diff.squeeze()
            except IndexError:
                intensity[change == date] = no_data
            else:
                intensity[change == date] = diff[change == date]

    return intensity


def count_nb_changes(arrays, dates, threshold, nb_samples, no_data):
    """ Count number of changes occurring in image time series

    Parameters
    ----------
    arrays
    dates
    threshold
    nb_samples
    no_data

    Returns
    -------

    """
    single_change = single_change_detection(arrays, dates, threshold, nb_samples, no_data)
    output = _multi_change(single_change,
                           np.asarray(arrays),
                           dates,
                           threshold,
                           nb_samples,
                           no_data)
    output = np.asarray([single_change] + output)
    nb_changes = np.sum(output != no_data, axis=0)

    if no_data != 0:
        nb_changes[nb_changes == 0] = no_data

    return nb_changes


def multi_change_detection(arrays, dates, threshold, nb_samples, no_data):
    """ Detect multiple changes in raster window

    Parameters
    ----------
    arrays: list or numpy.ndarray
    dates: list or numpy.ndarray
    threshold: float
    nb_samples: int
    no_data: int

    Returns
    -------

    """
    no_data_temp = 0
    multi_change = np.zeros((len(dates),
                             arrays[0].shape[0],
                             arrays[0].shape[1]))
    multi_change[0, :, :] = single_change_detection(arrays, dates,
                                                    threshold, nb_samples,
                                                    no_data=no_data_temp)
    output = _multi_change(multi_change[0, :, :],
                           np.asarray(arrays),
                           dates,
                           threshold,
                           nb_samples,
                           no_data=no_data_temp)

    if output:
        output = compress(np.asarray(output))
        multi_change[1:len(output) + 1, :, :] = output

    if no_data != 0:
        multi_change[multi_change == 0] = no_data

    return multi_change


def single_change_detection(arrays, dates, threshold, nb_samples, no_data):
    """ Detect single change in raster window

    Parameters
    ----------
    arrays: list or numpy.ndarray
    dates: list or numpy.ndarray
    threshold: float
    nb_samples: int
    no_data: int

    Returns
    -------

    """
    arrays = np.asarray(arrays)
    ci = np.ones(arrays[0].shape)
    change = np.zeros(arrays[0].shape)
    avg = np.mean(arrays, axis=0)
    cumsum = np.cumsum(arrays - avg, axis=0)
    rg = np.max(cumsum, axis=0) - np.min(cumsum, axis=0)

    rng = np.random.default_rng()
    bootstrap = rng.permutation(arrays)

    for _ in range(nb_samples):
        cumsum_bs = np.cumsum(bootstrap - avg, axis=0)
        rg_bs = np.max(cumsum_bs, axis=0) - np.min(cumsum_bs, axis=0)

        ci[rg_bs >= rg] -= 1/nb_samples  # >= and not strictly greater than (>)

        rng.shuffle(bootstrap)

    change[ci >= threshold] = 1
    single_change = change * dates[np.argmax(cumsum, axis=0)]

    if no_data != 0:
        single_change[single_change == 0] = no_data

    return single_change


def single_change_detection_tcs(arrays, dates, threshold_high, threshold_low, nb_samples, no_data):
    """ Detect single change in raster window for two thresholds

    Parameters
    ----------
    arrays: list or numpy.ndarray
    dates: list or numpy.ndarray
    threshold_high: float
    threshold_low: float
    nb_samples: int
    no_data: int

    Returns
    -------

    """
    arrays = np.asarray(arrays)
    arrays[arrays == 0] = -999

    ci = np.ones(arrays[0].shape)
    change_high = np.zeros(arrays[0].shape)
    change_low = np.zeros(arrays[0].shape)
    avg = np.mean(arrays, axis=0)

    cumsum = np.cumsum(arrays - avg, axis=0)
    rg = np.max(cumsum, axis=0) - np.min(cumsum, axis=0)

    rng = np.random.default_rng()
    bootstrap = rng.permutation(arrays)

    for _ in range(nb_samples):
        cumsum_bs = np.cumsum(bootstrap - avg, axis=0)
        rg_bs = np.max(cumsum_bs, axis=0) - np.min(cumsum_bs, axis=0)

        ci[rg_bs >= rg] -= 1/nb_samples  # >= and not strictly greater than (>)

        rng.shuffle(bootstrap)

    change_high[ci >= threshold_high] = 1
    change_low[ci >= threshold_low] = 1
    single_change_high = change_high * dates[np.argmax(cumsum, axis=0)]
    single_change_low = change_low * dates[np.argmax(cumsum, axis=0)]
    if no_data != 0:
        single_change_high[single_change_high == 0] = no_data
        single_change_low[single_change_low == 0] = no_data

    return np.stack((single_change_low, single_change_high))


def change_tendency(arrays, dates, threshold, nb_samples, no_data):
    """ Compute change in tendency

    Parameters
    ----------
    arrays
    dates
    threshold
    nb_samples
    no_data

    Returns
    -------

    """
    change = single_change_detection(arrays, dates, threshold, nb_samples, no_data)

    changes = np.tile(np.ma.masked_equal(change, no_data), (len(dates), 1, 1))
    mask_before = np.asarray([chg <= date for chg, date in zip(changes, dates)])
    mask_after = np.asarray([chg > date for chg, date in zip(changes, dates)])
    changes_after = np.ma.masked_where(mask_before, arrays)
    changes_before = np.ma.masked_where(mask_after, arrays)

    tendency = np.mean(changes_after, axis=0) - np.mean(changes_before, axis=0)
    tendency[~np.isfinite(tendency)] = no_data

    return tendency.filled(no_data)
