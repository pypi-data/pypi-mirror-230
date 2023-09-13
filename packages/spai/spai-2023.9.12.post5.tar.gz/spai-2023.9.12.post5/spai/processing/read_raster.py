# Updated read_raster function to handle invalid extensions
def read_raster(image_name, storage, bands=[8, 4]):
    ds = storage.read(image_name)
    if ds is None:
        raise TypeError("Not a valid raster file")
    raster = ds.read(bands)
    return ds, raster