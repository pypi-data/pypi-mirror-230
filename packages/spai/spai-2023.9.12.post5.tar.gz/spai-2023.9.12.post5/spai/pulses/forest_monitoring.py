import numpy as np
import geopandas as gpd

from ..processing import read_raster
from ..processing import normalised_difference
from ..processing import mask_raster
from ..processing import autocategorize1D
from ..processing import px_count
from ..processing import colorize_raster
from ..processing import save_table


def forest_monitoring(image_name, aoi_mask, storage):
    # read_raster image
    ds, raster = read_raster(image_name, storage)
    # calculate ndvi
    ndvi = normalised_difference(raster)

    # save_raster ndvi
    raster_name_ndvi = "ndvi.tif"
    storage.create(ndvi, raster_name_ndvi, ds=ds)

    # read_geojson aoi_mask
    aoi_mask_gdf = gpd.GeoDataFrame.from_features(aoi_mask["features"], crs=4326)

    # mask_raster ndvi with aoi_mask
    ndvi_masked, out_transform = mask_raster(raster_name_ndvi, aoi_mask_gdf, storage)

    # save_raster ndvi_masked
    raster_name_ndvi_masked = "ndvi_masked.tif"
    storage.create(ndvi_masked, raster_name_ndvi_masked, ds=ds)

    # autocategorize1D ndvi
    ndvi_categorized = autocategorize1D(ndvi)

    # save_raster ndvi_categorized
    raster_name_ndvi_categorized = "ndvi_categorized.tif"
    storage.create(ndvi_categorized, raster_name_ndvi_categorized, ds=ds)

    # apply_threshold to ndvi_categorized
    threshold = 3
    vegetation = ndvi_categorized >= threshold
    vegetation = vegetation.astype(int)

    # save_raster vegetation
    raster_name_vegetation = "vegetation.tif"
    storage.create(vegetation, raster_name_vegetation, ds=ds)

    # mask_raster vegetation with aoi_mask
    vegetation_masked, out_transform = mask_raster(
        raster_name_vegetation, aoi_mask_gdf, storage
    )

    # save_raster vegetation_masked
    raster_name_vegetation_masked = "vegetation_masked.tif"
    storage.create(vegetation_masked, raster_name_vegetation_masked, ds=ds)

    # colorize_raster vegetation_masked
    vegetation_masked_rgb = colorize_raster(vegetation_masked)

    # save_raster vegetation_masked_rgb
    raster_name_vegetation_masked_rgb = "vegetation_masked_rgb.tif"
    storage.create(vegetation_masked_rgb, raster_name_vegetation_masked_rgb, ds=ds)

    # mask_raster ndvi_categorized with aoi_mask
    quality_mask, out_transform = mask_raster(
        raster_name_ndvi_categorized, aoi_mask_gdf, storage
    )

    # save_raster quality_mask
    raster_name_quality_mask = "quality_masked.tif"
    storage.create(quality_mask, raster_name_quality_mask, ds=ds)

    # colorize_raster quality_mask
    quality_mask_rgb = colorize_raster(
        quality_mask, colors=["black", "orangered", "yellow", "lawngreen", "darkgreen"]
    )

    # save_raster quality_mask_rgb
    raster_name_quality_mask_rgb = "quality_masked_rgb.tif"
    storage.create(quality_mask_rgb, raster_name_quality_mask_rgb, ds=ds)

    # px_count vegetation_masked
    growth = px_count(vegetation_masked, values=[0, 1])

    # div growth
    growth_hectarias = np.divide(
        growth, 100, out=np.zeros_like(growth, dtype=np.float64), where=100 != 0
    )

    # save_table growth
    growth_table_name = "AOI_Vegetation_Growth.json"
    growth_columns = ["Not Vegetation Ha", "Vegetation Ha", "Total"]
    save_table(
        data=growth_hectarias,
        columns=growth_columns,
        table_name=growth_table_name,
        storage=storage,
    )

    # px_count quality_mask
    quality = px_count(quality_mask, values=[0, 1, 2, 3])

    # div quality
    quality_hectarias = np.divide(
        quality, 100, out=np.zeros_like(quality, dtype=np.float64), where=100 != 0
    )

    # save_table quality
    quality_table_name = "AOI_Vegetation_Quality.json"
    quality_columns = [
        "Bare Ground",
        "Sparse or Unhealthy Vegetation",
        "Healthy Vegetation",
        "Very Health Vegetation",
        "Total",
    ]
    save_table(
        data=quality_hectarias,
        table_name=quality_table_name,
        columns=quality_columns,
        storage=storage,
    )
