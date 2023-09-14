import multiprocessing as mp
import os
import re
import warnings
from functools import partial

import numpy as np
from pyrasta.raster import Raster
from tqdm import tqdm

try:
    import gdal
except ModuleNotFoundError:
    from osgeo import gdal

warnings.filterwarnings("ignore")


PG_DESCRIPTION = dict(single_change_detection="single change",
                      multi_change_detection="multi change",
                      change_intensity="change intensity",
                      change_tendency="change tendency",
                      count_nb_changes="number of changes")


def cdtec_apply(fhandles, in_dir, out_dir, c_levels,
                out_file_prefix="", data_types=None,
                max_samples=500, nb_processes=mp.cpu_count(),
                window_size=100, chunksize=1, no_data=0):
    """ Apply list of cdtec.change functions, with corresponding list of confidence levels

    Parameters
    ----------
    fhandles
    in_dir: str
        Absolute path to input directory
    out_dir: str
        Absolute path to output directory
    out_file_prefix: str
        Prefix for output file(s) written to output directory out_dir
    c_levels
    data_types
    max_samples
    nb_processes
    window_size
    chunksize
    no_data

    Returns
    -------

    """
    if out_file_prefix:
        out_file_prefix = out_file_prefix + "_"

    images = []
    dates = []

    for _, _, file in os.walk(in_dir):
        for name in file:
            if not name.startswith("."):
                images.append(os.path.join(in_dir, name))
                dates.append(int(re.search(r'_(\d{8})T', name)[1]))

    images.sort()

    sources = [Raster(img) for img in images]

    if data_types is None:
        data_types = ["float32"] * len(fhandles)

    pg = tqdm(total=len(fhandles) * len(c_levels),
              desc="Compute change detection")

    for fhandle, dtype in zip(fhandles, data_types):
        for c_level in c_levels:

            result = cdtec_run(fhandle, sources, dates, c_level,
                               max_samples, nb_processes,
                               window_size, chunksize, dtype,
                               no_data, progress_bar=True)

            result.to_file(os.path.join(out_dir,
                                        "%s%s_%d.tif" % (out_file_prefix,
                                                         fhandle.__name__,
                                                         c_level * 100)))
            pg.update(1)

    pg.close()


def cdtec_run(fhandle, sources, dates, c_level, max_samples=500,
              nb_processes=mp.cpu_count(), window_size=100,
              chunksize=1, data_type="float32", no_data=0,
              progress_bar=True):
    """ Run detection change function

    Parameters
    ----------
    fhandle: function
        Change detection function to be applied
    sources: list[pyrasta.raster.RasterBase]
        list of rasters
    dates: list of numpy.ndarray
        list of dates corresponding to rasters
    c_level: float
        Confidence level (between 0 and 1)
    max_samples: int
        Max number of samples for bootstrapping
    nb_processes: int
        Number of processes for multiprocessing
    window_size: int or tuple(int, int)
        Size of window for raster calculation
    chunksize: int
        Chunk size for multiprocessing imap function
    data_type: str
        Data type for output raster
    no_data: int
        No data value
    progress_bar: bool
        if True, display progress bar

    Returns
    -------

    """
    dates = np.asarray(dates)
    nb_samples = min(max_samples, np.math.factorial(len(sources)))

    if progress_bar:
        desc = f"Compute {PG_DESCRIPTION[fhandle.__name__]} " \
               f"(CL=%s)" % ("%.2f" % c_level).lstrip('0')
    else:
        desc = None

    change = Raster.raster_calculation(sources, partial(fhandle,
                                                        dates=dates,
                                                        threshold=c_level,
                                                        nb_samples=nb_samples,
                                                        no_data=no_data),
                                       output_type=gdal.GetDataTypeByName(data_type),
                                       window_size=window_size,
                                       nb_processes=nb_processes,
                                       chunksize=chunksize,
                                       no_data=no_data,
                                       description=desc)

    return change
