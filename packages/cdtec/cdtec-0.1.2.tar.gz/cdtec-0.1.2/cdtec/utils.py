# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

import numpy as np


def compress(array):
    """ Compress 3D array (i.e. trim leading/trailing and inner zeros) along first axis

    Parameters
    ----------
    array

    Returns
    -------

    """
    if array.ndim != 3:
        return np.expand_dims(array, axis=0)

    output = np.flip(np.sort(array, axis=0), axis=0)
    output = output[output.any(axis=(1, 2)), :, :]

    return output


def moving_average(array, window, axis):
    """ Compute moving average over nd array

    Parameters
    ----------
    array: numpy.ndarray
        Input array
    window: int
        Size of moving window
    axis: int
        Axis along which moving window must be applied

    Returns
    -------

    """
    def convolve(arr):
        return np.convolve(arr, np.ones((window,)))

    convolved_array = np.apply_along_axis(convolve, axis=axis, arr=array)[: 1 - window]
    moving_avg = convolved_array/np.minimum(window, np.arange(array.shape[axis]) + 1)

    return moving_avg
