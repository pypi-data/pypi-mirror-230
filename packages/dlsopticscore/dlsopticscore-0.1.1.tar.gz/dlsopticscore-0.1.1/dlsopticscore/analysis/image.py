import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import numpy as np

def find_peak(data):
    neighborhood_size = 50
    threshold = 10

    data_max = filters.maximum_filter(data, neighborhood_size)
    maxima = (data == data_max)
    data_min = filters.minimum_filter(data, neighborhood_size)
    diff = ((data_max - data_min) > threshold)
    maxima[diff == 0] = 0

    labeled, num_objects = ndimage.label(maxima)
    slices = ndimage.find_objects(labeled)

    x, y = [], []

    for dy,dx in slices:
        x_center = (dx.start + dx.stop - 1)/2
        y_center = (dy.start + dy.stop - 1)/2

        x.append(x_center)
        y.append(y_center)

    peak_x = np.mean(x) if len(x) else np.nan
    peak_y = np.mean(y) if len(y) else np.nan
    peak_max = np.max(data_max)

    return peak_x, peak_y, peak_max
