# from rasterio.mask import mask # así no podemos hacer el patch
import rasterio 

def mask_raster(raster_name, gdf, storage):
    # crop image to geometry
    ds = storage.read(raster_name)
    if ds is None:
        raise Exception("Raster not found")
    geometry = gdf.geometry
    # return mask_a_raster(ds,geometry)
    return rasterio.mask.mask(ds, geometry) # importar así para testing

