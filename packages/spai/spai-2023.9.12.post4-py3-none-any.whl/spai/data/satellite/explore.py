from .sentinelhub import SHExplorer
from .utils import create_aoi_geodataframe
from datetime import datetime, timedelta


def explore_satellite_images(aoi, time_interval=None, sensor="S2L2A", **kargs):
    if time_interval is None:
        # last month
        now = datetime.now()
        last_months = now - timedelta(days=30)
        time_interval = (last_months.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"))
    # TODO: validate time format
    gdf = create_aoi_geodataframe(aoi)
    if isinstance(gdf, list):
        return gdf
    explorer = SHExplorer(time_interval, sensor, **kargs)
    results = explorer.search(gdf)
    return results
