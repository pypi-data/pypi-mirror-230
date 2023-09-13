import numpy as np


def px_count(raster, values=None):
    flattened_raster = raster.flatten()
    counts = np.bincount(flattened_raster.astype(np.int64))

    if values is None:
        total_count = np.sum(counts)
        return np.append(counts, total_count)
    elif len(values) == 0:
        non_zero_indexes = [index for index, value in enumerate(counts) if value != 0]
        unique_count = len(non_zero_indexes)
        return np.append(counts, unique_count)
    else:
        desired_counts = []
        for value in values:
            if value < len(counts):
                desired_counts.append(counts[value])
            else:
                desired_counts.append(0)
        total_count = np.sum(desired_counts)
        desired_counts.append(total_count)
        return np.array(desired_counts)
