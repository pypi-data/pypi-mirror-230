"""
Provides a simple way to visualize query results on a map.  For instructions see [Kepler.GL](https://kepler.gl/) user guide.

:::{attention}
This module should be considered experimental and subject to change.
:::
"""

import logging
from copy import deepcopy
from typing import List, Optional, Union

import geopandas as gpd
import pandas as pd
from keplergl import KeplerGl
from shapely.geometry import Polygon

from dfi import validate
from dfi._services.polygons import Polygons, from_bbox_to_polygon_list
from dfi.connect import Connect
from dfi.models import Polygon as ModelPolygons

_logger = logging.getLogger(__name__)


class Show:
    """
    Visualisation methods to build use case on top of the queries from DFI.

    It can be accessed via the a dfi.Client class instance or it must be instantiated
    with a dfi.Connect instance as argument.

    :param dfi_conn: Instance of a Connect with the credentials and namespace of the DFI connection.

    :exmaple:
    Access via the Client class:

    ```python
    from dfi import Client

    dfi = Client(dfi_token, instance_name, namespace, base_url)

    dfi.show.map() # creates an empty Kepler map
    ```
    """

    def __init__(self, dfi_conn: Connect) -> None:
        self.conn: Connect = dfi_conn
        self.polygons = Polygons(self.conn)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def map(
        self,
        list_polygons: Optional[List[ModelPolygons]] = None,
        list_polygons_by_names: Optional[List[str]] = None,
        df_records: Optional[pd.DataFrame] = None,
        list_dfs: Optional[Union[gpd.GeoDataFrame, pd.DataFrame]] = None,
        map_height: int = 1200,
        config: Optional[dict] = None,
    ) -> KeplerGl:
        """
        Helper method to crete a kepler map with the given input layers, to reproduce proposed
        examples in the example notebooks.

        :param list_polygons: List of polygons, as list of vertices [[lon1, lat1], [lon2, lat2], ...].
        :param list_polygons_by_names: List of polygon names as they are named in the auxiliary Polygon DB.
        :param df_records: Dataframe of records with record_id, timestamp, latitude, longitude as its columns.
        :param list_dfs: Generic list of any dataframe or geodataframe to be visualised on the map.
        :param map_height: Parameter passed to the KeplerGl instance as it is, overriding the default.
        :param config: A KeplerGL map config.  See [KeplerGL docs](https://github.com/keplergl/kepler.gl/tree/master/bindings/kepler.gl-jupyter#for-jupyter-notebook-and-jupyterlab) for more info.
        :returns: Instance of a KeplerGL map with the given data to visualise.
        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)

        df = dfi.get.records(
            entities = ["a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d8"]
        )

        dfi.show.map(
            df_records=df
        )
        ```

        :::{note}
        For instructions see [Kepler.GL](https://kepler.gl/) user guide.
        :::
        """
        if list_polygons is None:
            list_polygons = []

        list_polygons_as_vertices = []
        for poly in list_polygons:
            # from bounding boxes to vertices
            validate.polygon(poly)
            if isinstance(poly[0], float):
                list_polygons_as_vertices += [from_bbox_to_polygon_list(poly)]
            else:
                list_polygons_as_vertices += [poly]

        dict_polygons = {f"polygon {idx}": poly for idx, poly in enumerate(list_polygons_as_vertices)}

        if list_polygons_by_names is not None:
            dict_polygons.update(
                {poly_name: self.polygons.get_vertices(poly_name) for poly_name in list_polygons_by_names}
            )

        kepler_data = {}

        if len(dict_polygons) > 0:
            kepler_data.update(
                {
                    "polygons": gpd.GeoDataFrame(
                        dict_polygons.keys(),
                        geometry=[Polygon(x) for x in dict_polygons.values()],
                    )
                }
            )

        if df_records is not None:
            validate.df_records(df_records)
            kepler_data.update({"records": df_records.copy()})

        if list_dfs is not None:
            for idx, df in enumerate(list_dfs):
                kepler_data.update({f"df_{idx}": df.copy()})

        if config is None:
            return KeplerGl(data=deepcopy(kepler_data), height=map_height)
        return KeplerGl(data=deepcopy(kepler_data), height=map_height, config=config)
