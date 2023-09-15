from typing import TypeVar
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon, shape
from shapely import wkt, wkb
import folium
import pandas as pd
from pandas_flavor import register_dataframe_method, register_dataframe_accessor
from .connection import database_url, query
import matplotlib


from pandas import *
from geopandas import *


def create_marker_icon(color):
    # Define a function to create a custom marker icon
    return folium.Icon(color=color, icon="circle", prefix="fa")


def marker(location, color="red", popup=None, tooltip=None):
    return folium.Marker(
        location=location, icon=create_marker_icon(color), popup=popup, tooltip=tooltip
    )


def read_csv(
    file,
    latitude="latitude",
    longitude="longitude",
    geometry=["geometry", "geom", "wkb_geometry"],
    format="",
    **kwargs
) -> gpd.GeoDataFrame:
    csv = pd.read_csv(file, **kwargs)
    try:
        return csv.geo(
            latitude=latitude,
            longitude=longitude,
            geometry=geometry,
            format=format,
            **kwargs
        )
    except Exception as e:
        print(e)
        return csv


T = TypeVar("T")


def read_sql(
    sql,
    database=database_url(),
    latitude="latitude",
    longitude="longitude",
    geometry=["geometry", "geom", "wkb_geometry"],
    format="",
    **kwargs
) -> gpd.GeoDataFrame:
    cols, results = query(sql, database)
    sql = pd.DataFrame(results, columns=[col[0] for col in cols])
    try:
        return sql.geo(
            latitude=latitude,
            longitude=longitude,
            geometry=geometry,
            format=format,
            **kwargs
        )
    except Exception as e:
        print(e)
        return sql


def read_geojson(url) -> gpd.GeoDataFrame:
    import requests
    import os
    import tempfile

    text = requests.get(url).content
    # save text to file in os temp directory
    path = os.path.join(tempfile.gettempdir(), "reading.geojson")
    with open(path, "w") as f:
        f.write(str(text, encoding="utf-8"))
    return gpd.read_file(path, driver="GeoJSON")


def read_storage(bucket: str, path: str) -> gpd.GeoDataFrame:
    from .db import supabase

    url = supabase.storage.get_bucket(bucket).get_public_url(path)
    return read_geojson(url)


@register_dataframe_method
def to_storage(df: DataFrame, bucket: str, storage_path: str):
    import tempfile
    import os
    from .db import supabase

    path = os.path.join(tempfile.gettempdir(), "writing.geojson")
    df.to_file(path, driver="GeoJSON")
    supabase.storage.get_bucket(bucket).remove([storage_path])
    supabase.storage.get_bucket(bucket).upload(storage_path, path)


@register_dataframe_accessor("geo")
class GeoDataFrameAccessor:
    def __init__(self, df):
        self._df = df

    def __call__(self, *args, **kwargs):
        self._df = create_geometry_column(self._df, *args, **kwargs)
        return gpd.GeoDataFrame(self._df, crs="EPSG:4326")


def parse_geometry(g: str):
    if g.startswith("SRID"):
        g = g.split(";")[1]
        return wkt.loads(g)
    elif (
        g.startswith("POLYGON") or g.startswith("MULTIPOLYGON") or g.startswith("POINT")
    ):
        return wkt.loads(g)
    elif g.startswith("{"):
        return shape(g)
    else:
        return wkb.loads(g)


format_map = {"geojson": shape, "wkt": wkt.loads, "wkb": wkb.loads, "": parse_geometry}


def create_geometry_column(
    df: pd.DataFrame,
    format="",
    geometry=["geometry", "geom", "wkb_geometry"],
    latitude="latitude",
    longitude="longitude",
):
    df = df.copy()
    if len(df) == 0:
        raise Exception("No data in Dataset to create geometry")

    if type(geometry) == str and geometry in df:
        if format in format_map:
            df.loc[:, "geometry"] = df.loc[:, geometry].apply(format_map[format])
        else:
            df.loc[:, "geometry"] = df.loc[:, geometry]
        return df

    for col in geometry:
        if col in df:
            if format in format_map:
                df.loc[:, "geometry"] = df.loc[:, col].apply(format_map[format])
            else:
                df.loc[:, "geometry"] = df.loc[:, col]
            return df

    if longitude in df and latitude in df:
        df.loc[:, longitude] = df[longitude].apply(
            lambda x: "0.0" if x == "" or x is None else x
        )
        df.loc[:, latitude] = df[latitude].apply(
            lambda x: "0.0" if x == "" or x is None else x
        )
        geom = [Point(xy) for xy in zip(df[longitude], df[latitude])]
        df.loc[:, "geometry"] = geom
        return df

    if "geometry" not in df:
        raise Exception(
            "No geometry column found in Dataset. Please provide a geometry column or a latitude and longitude column"
        )

    return df

    # # Create a GeoDataFrame from the DataFrame
    # gdf = gpd.GeoDataFrame(df, crs='EPSG:4326')
    # return gdf


@register_dataframe_method
def map_it(
    df: pd.DataFrame,
    format="",
    tooltip="name",
    geometry=["geometry", "geom", "wkb_geometry"],
    map=None,
    color="green",
    colormap="viridis",
    heatmap=None,
    opacity=0.5,
    zoom_level=5,
    center=[20.5937, 78.9629],
):
    if isinstance(df, gpd.GeoDataFrame):
        gdf = df
    else:
        gdf = df.geo(format=format, geometry=geometry)

    geometry = "geometry"

    _map = (
        map if map is not None else folium.Map(location=center, zoom_start=zoom_level)
    )
    errs = []

    # Check if heatmap_property is provided
    if heatmap is not None:
        # Retrieve the minimum and maximum values of the heatmap property
        min_value = gdf[heatmap].min()
        max_value = gdf[heatmap].max()

        normalize = matplotlib.colors.Normalize(vmin=min_value, vmax=max_value)
        # Create a colormap based on the provided colormap name
        colormap = matplotlib.colormaps.get_cmap(colormap)

        # Function to get the color based on the heatmap value
        def get_color(heatmap_value):
            return matplotlib.colors.to_hex(colormap(normalize(heatmap_value)))

    else:

        def get_color(x):
            return color

    def style_function(x):
        if heatmap is not None and heatmap in x:
            heatmap_value = x[heatmap]
            return {
                "fillColor": get_color(heatmap_value),
                "fillOpacity": opacity,
            }

        return {
            "fillColor": color,
            "fillOpacity": opacity,
        }

    # Add the points to the map
    for idx, row in gdf.iterrows():
        if not row[geometry].is_empty:
            geom = row[geometry]
            if isinstance(geom, Point):
                if tooltip in row:
                    _tooltip = row[tooltip]
                elif "{" in tooltip:
                    _tooltip = tooltip.format(**row.to_dict())
                else:
                    _tooltip = "{},{}".format(row[geometry].x, row[geometry].y)
                # Set the color based on the heatmap property value
                if heatmap is not None:
                    heatmap_value = row[heatmap]
                    point_color = get_color(heatmap_value)
                else:
                    point_color = color
                marker(
                    location=[row[geometry].y, row[geometry].x],
                    tooltip=_tooltip,
                    color=point_color,
                ).add_to(_map)
            if isinstance(geom, Polygon) or isinstance(geom, MultiPolygon):
                if tooltip in row:
                    _tooltip = row[tooltip]
                elif "{" in tooltip:
                    _tooltip = tooltip.format(**row.to_dict())
                else:
                    _tooltip = ""

                folium.GeoJson(
                    data=gpd.GeoSeries(
                        geom, [0] if heatmap is None else [row[heatmap]]
                    ).to_json(),
                    tooltip=_tooltip,
                    style_function=style_function,
                ).add_to(_map)
            else:
                if tooltip in row:
                    _tooltip = row[tooltip]
                elif "{" in tooltip:
                    _tooltip = tooltip.format(**row.to_dict())
                else:
                    _tooltip = ""

                folium.GeoJson(
                    data=gpd.GeoSeries(
                        geom, [0] if heatmap is None else [row[heatmap]]
                    ).to_json(),
                    tooltip=_tooltip,
                    style_function=style_function,
                ).add_to(_map)
        else:
            errs.append(idx)

    return _map
