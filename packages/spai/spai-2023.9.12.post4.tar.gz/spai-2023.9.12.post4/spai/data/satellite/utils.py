import os
import geopandas as gpd
import geojson
from shapely.geometry import box
from shapely.geometry.polygon import Polygon
import requests


def validate_coords(coords):
    # Coordinates of points of a polygon: [[lon1,lat1],[lon2,lat2], ... ,[lonN,latN]]
    for coord in coords:
        # check that each coord is a list of 2 coordinates
        if len(coord) != 2:
            raise Exception("each coord must be a list of 2 coordinates")
        # check that each coordinate is a float
        if not isinstance(coord[0], float) or not isinstance(coord[1], float):
            raise Exception("each coordinate must be a float")
        lon = coord[0]
        lat = coord[1]

        # check lat and long ranges
        if lon < -180 or lon > 180 or lat < -90 or lat > 90:
            raise Exception("each coordinate must be a valid lat/long")

    return coords


def validate_bounds(bounds):
    # check that bounds is a list
    if len(bounds) != 4 or not isinstance(bounds, tuple):
        raise Exception(
            "bounds must be a tuple of 4 points: (minlon, minlat, maxlon, maxlat))"
        )
    # check that each bound is a float
    for bound in bounds:
        if not isinstance(bound, float):
            raise Exception("each bound must be a float")
    # check lat and long ranges
    minlon = bounds[0]
    minlat = bounds[1]
    maxlon = bounds[2]
    maxlat = bounds[3]

    if minlat < -90 or minlat > 90 or maxlat < -90 or maxlat > 90:
        raise Exception("each latitude must be a valid lat/long")
    if minlon < -180 or minlon > 180 or maxlon < -180 or maxlon > 180:
        raise Exception("each longitude must be a valid lat/long")
    # check that minlat < maxlat and minlng < maxlng
    if minlon > maxlon or minlat > maxlat:
        raise Exception(
            "minlat must be less than maxlat and minlng must be less than maxlng"
        )
    return bounds


def create_aoi_geodataframe(obj):
    # obj can be a :
    # GeoDataFrame,
    # GeoJSON file,
    # Path to a GeoJSON file,
    # Polygon of Shapely (Bounding Box),
    # List of Coords of a (Bounding Box),
    # Location name (string)

    # return a GeoDataFrame of the Bounding Box of the obj or a list of gdfs if obj is a location name and there are more than one relation

    if (
        isinstance(obj, str)
        and not os.path.isfile(obj)
        and not obj.endswith(".geojson")
    ):
        # case 1: obj is a location name (e.g. "Madrid")
        obj = get_box_or_gdfs_by_place_name(
            obj
        )  # return Box of Shapely or list of gdfs
        if isinstance(obj, list):
            return obj

    elif isinstance(obj, list):
        # case 2: obj is a list of coords of a Polygon: [[lat1,long1],[lat2,long2],...,[latN,longN]]
        coords = validate_coords(obj)
        poly = Polygon(coords)
        bounds = poly.bounds
        obj = box(*bounds)  # return Box of Shapely

    if isinstance(obj, tuple):
        # case 3: obj is a tuple of bounds: (minlat, minlng, maxlat, maxlng)
        bounds = validate_bounds(obj)
        obj = box(*bounds)  # return Box of Shapely

    if isinstance(obj, Polygon):
        # case 4: obj is a Box of Shapely: Polygon[[lat1,long1],[lat2,long2],[lat3,long3],[lat4,long4]]
        bounds = obj.bounds
        validate_bounds(bounds)
        return gpd.GeoDataFrame(geometry=[obj], crs=4326)

    if isinstance(obj, gpd.GeoDataFrame):
        # case 5: obj is a GeoDataFrame
        return obj.to_crs(4326)

    if (
        isinstance(obj, dict)
        and obj.get("type") == "FeatureCollection"
        and "features" in obj
    ):
        # case 6: obj is a GeoJSON file
        if obj["type"] == "Polygon":
            for coords in obj["coordinates"][0]:
                validate_coords(coords)
        elif obj["type"] == "MultiPolygon":
            for _coords in obj["coordinates"][0]:
                for coords in _coords:
                    validate_coords(coords)
        return gpd.GeoDataFrame.from_features(obj, crs=4326)

    if isinstance(obj, str) and os.path.isfile(obj) and obj.endswith(".geojson"):
        # case 7: obj is a path to GeoJSON file
        geojson_file = geojson.load(open(obj))
        if geojson_file["type"] == "Polygon":
            for coords in geojson_file["coordinates"][0]:
                validate_coords(coords)
        elif geojson_file["type"] == "MultiPolygon":
            for _coords in geojson_file["coordinates"][0]:
                for coords in _coords:
                    validate_coords(coords)
        return gpd.GeoDataFrame.from_features(geojson_file, crs=4326)

    raise Exception(f"location {obj} not supported")


def get_bb_by_city_name(city_name):
    base_url = "https://nominatim.openstreetmap.org"
    format_out = "json"
    limit = 10

    # Construct the API request URL
    url = f"{base_url}/search?city={city_name}&format={format_out}&limit={limit}"

    # Send the API request
    response = requests.get(url).json()

    results = []
    if len(response) == 0:
        raise Exception("No results found")
    for result in response:
        if "boundingbox" in result:
            bounding_box = result["boundingbox"]
            if len(bounding_box) == 4:
                min_lon, max_lon, min_lat, max_lat = map(float, bounding_box)
                results.append(
                    {
                        "name": f"{result['display_name']}",
                        "bbox": box(min_lat, min_lon, max_lat, max_lon),
                    }
                )

    return results


def get_box_or_gdfs_by_place_name(place_name):
    if not isinstance(place_name, str):
        raise Exception("place_name must be a string")
    results = get_bb_by_city_name(place_name)
    gdfs = []
    if len(results) == 1:
        # Only one result, access the bounding box directly
        return results[0]["bbox"]
    else:
        # Multiple results, iterate over the dictionary
        for dict in results:
            gdf = gpd.GeoDataFrame(geometry=[dict["bbox"]], crs=4326)
            gdfs.append({"name": dict["name"], "gdf": gdf})
        return gdfs
