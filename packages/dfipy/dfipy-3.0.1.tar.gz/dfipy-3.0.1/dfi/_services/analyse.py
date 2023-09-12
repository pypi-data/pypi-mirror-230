"""
Common analytical queries and transformations of results.

:::{attention}
This module should be considered experimental and subject to change.
:::
"""

import logging
from datetime import timedelta
from typing import Optional

import geopandas as gpd
import h3.api.numpy_int as h3
import pandas as pd
from shapely.geometry import Polygon

from dfi import models, validate
from dfi._services.get import Get
from dfi.connect import Connect

_logger = logging.getLogger(__name__)


class Analyse:
    """
    Class with analytical methods to build use cases on top of the DFI's queries.

    It can be accessed via the a dfi.Client class instance or it must be instantiated
    with a dfi.Connect instance as argument.

    :param dfi_conn: Instance of a Connect with the credentials and namespace of the DFI connection.
    :example:
    ```python
    from dfi import Client

    dfi = Client(dfi_token, instance_name, namespace, base_url)
    dfi.analyse.records_in_hexagons(uid, resolution, period)
    ```
    """

    def __init__(self, dfi_conn: Connect) -> None:
        self.conn: Connect = dfi_conn
        self.get = Get(self.conn)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def add_spatiotemporal_hashing(
        self,
        df_records: pd.DataFrame,
        h3_resolution: int,
        time_resolution_min: int,
    ) -> gpd.GeoDataFrame:
        """
        Finds the unique space-time hashes for an entity_id.

        A space-time hash is created for each record from the H3 id and time period

        | entity_id                            | longitude | latitude | timestamp               |
        |--------------------------------------|-----------|----------|-------------------------|
        | a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d8 | -0.0769   | 51.5273  | 2022-01-01 12:32:30.000 |


        With H3 resolution 10 and a time period of 5 minutes the following are appended as columns to the dataframe.

        | h3_id           | period_start          | period_end          | geometry                                                                                                                                                                                                                                                                                      |
        |-----------------|---------------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | 8a194ad3478ffff | 2022-01-01 12:30:00 | 2022-01-01 12:35:00 | POLYGON ((-0.0763811054263752 51.52815508753436, -0.0773394908309314 51.52798511308078, -0.0775149002044645 51.52734623441407, -0.0767319401124731 51.526877335658725, -0.0757735765036792 51.52704731096069, -0.0755981511914388 51.527686184169575, -0.0763811054263752 51.52815508753436)) |


        :param df_records: Dataframe with the records we want to hash.
        :param h3_resolution: Uber's H3 h3_resolution. Allowed numbers are > 1 and < 15.
        :param time_resolution_min: Time interval in minutes for timestamp binning.

        :returns: A copy of df_records casted to a GeoDataFrame with 3 extra columns: [hex_id, period_start, period_end] and
        with "geometry" column the geometry of the H3 hexagon where the record appeared.

        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)

        df_records = dfi.get.records(entities=[entity_id], time_interval=(start_time, end_time))
        dfi.analyse.add_spatiotemporal_hashing(df_records, h3_resolution=11, time_resolution_min=15)
        ```
        """
        validate.df_records(df_records)
        validate.h3_resolution(h3_resolution)

        df_records["hex_id"] = [
            h3.geo_to_h3(lat, lon, h3_resolution) for lat, lon in zip(df_records["latitude"], df_records["longitude"])
        ]
        df_records = df_records.assign(period_start=lambda df: df["timestamp"].round(f"{time_resolution_min}min"))
        df_records = df_records.assign(period_end=lambda df: df.period_start + timedelta(minutes=time_resolution_min))

        return gpd.GeoDataFrame(
            df_records,
            geometry=df_records["hex_id"].apply(lambda idx: Polygon(h3.h3_to_geo_boundary(idx, geo_json=True))),
        )

    def records_for_entity_id_with_spatiotemporal_hashing(
        self,
        entity_id: str,
        h3_resolution: int,
        time_resolution_min: int,
        time_interval: Optional[models.TimeInterval] = None,
        polygon: Optional[models.Polygon] = None,
    ) -> gpd.GeoDataFrame:
        """
        Finds the unique space-time hashes for an entity_id.

        A space-time hash is created for each record from the H3 id and time period

        | entity_id                            | longitude | latitude | timestamp               |
        |--------------------------------------|-----------|----------|-------------------------|
        | a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d8 | -0.0769   | 51.5273  | 2022-01-01 12:32:30.000 |

        With H3 resolution 10 and a time period of 5 minutes the following are appended as columns to the dataframe.

        | h3_id           | period_start          | period_end          | geometry                                                                                                                                                                                                                                                                                      |
        |-----------------|---------------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | 8a194ad3478ffff | 2022-01-01 12:30:00 | 2022-01-01 12:35:00 | POLYGON ((-0.0763811054263752 51.52815508753436, -0.0773394908309314 51.52798511308078, -0.0775149002044645 51.52734623441407, -0.0767319401124731 51.526877335658725, -0.0757735765036792 51.52704731096069, -0.0755981511914388 51.527686184169575, -0.0763811054263752 51.52815508753436)) |


        :param entity_id: unique identifier of a device we want to analyse.
        :param h3_resolution: Uber's H3 h3_resolution. Allowed numbers are > 1 and < 15.
        :param time_resolution_min: Time interval in minutes for timestamp binning.
        :param time_interval: Tuple of time bounds where (lower bound, upper bound).
        :param polygon: List of vertices [[lon1, lat1], [lon2, lat2], ...] or a list of four
                floats representing the bounding box extremes as [lon_min, lat_min, lon_max, lat_max].
                Non valid input will raise an error.

        :returns:
        A dataframe with the history of the loaded records from DFI by the constraints space and time,
        with extra columns with the binning of H3 resolution and time resolution.

        From there you can get the unique hexagons from where the devices are appearing.

        :raises `DFIInputValueError`: If `time_interval` or `polygon` are ill-formed.
        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)

        entity="299eb59a-e47e-48c0-9ad5-89a9ce1303f4"
        polygon = [[-0.1169,51.5096], [-0.1184,51.5090], [-0.1167,51.5074], [-0.1153,51.5079], [-0.1169,51.5096]]
        start_time = datetime.strptime("2022-01-01T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = datetime.strptime("2022-01-01T08:30:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")

        dfi.analyse.records_for_entity_id_with_spatiotemporal_hashing(
            entity_id=entity,
            h3_resolution=11,
            time_resolution_min=15,
            time_interval=(start_time, end_time),
            polygon=polygon
        )
        ```
        """
        df_records = self.get.records(entities=[entity_id], polygon=polygon, time_interval=time_interval)

        if len(df_records) == 0:
            _logger.debug("No history found for entity %s", entity_id)
            return gpd.GeoDataFrame(
                columns=[
                    "entity_id",
                    "latitude",
                    "longitude",
                    "timestamp",
                    "hex_id",
                    "period_start",
                    "period_end",
                ]
            )

        return self.add_spatiotemporal_hashing(
            df_records,
            h3_resolution=h3_resolution,
            time_resolution_min=time_resolution_min,
        )

    def add_heatmap_aggregation(
        self,
        df_records: pd.DataFrame,
        h3_resolution: int,
    ) -> pd.DataFrame:
        """
        Aggregates the records by the H3 hexagons at the given resolution.

        :param df_records: Dataframe with the records we want to aggregate.
        :param h3_resolution: Uber's H3 resolution. Allowed numbers are > 1 and < 15.

        :returns: The given dataframe with extra `hex_id`, `num_records` and `color` columns.

        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)

        df_records = dfi.get.records(
            entities=[entity_id],
            time_interval=(start_time, end_time)
        )
        dfi.analyse.heatmap_aggregation(df_records, h3_resolution=11)
        ```
        """
        return (
            df_records.assign(
                hex_id=lambda df: [
                    h3.geo_to_h3(lat, lon, resolution=h3_resolution)
                    for lat, lon in zip(df["latitude"], df["longitude"])
                ]
            )
            .pipe(_aggregate_records, "hex_id")
            .assign(hex_id=lambda df: df.hex_id.map(hex).str[2:])
        )

    def records_for_entity_id_with_heatmap_aggregation(
        self,
        entity_id: str,
        h3_resolution: int,
        time_interval: Optional[models.TimeInterval] = None,
        polygon: Optional[models.Polygon] = None,
    ) -> pd.DataFrame:
        """
        Aggregates the records by the H3 hexagons at the given resolution, from the parameters
        to a DFI query (entity_id, polygon, start_time, end_time)

        :param entity_id: unique identifier of a device we want to analyse.
        :param h3_resolution: Uber's H3 h3_resolution. Allowed numbers are > 1 and < 15.
        :param time_interval: Tuple of time bounds where (lower bound, upper bound).
        :param polygon:  List of vertices [[lon1, lat1], [lon2, lat2], ...] or a list of four
            floats representing the bounding box extremes as [lon_min, lat_min, lon_max, lat_max].
            Non valid input will raise an error.

        :returns: Returns the queried records dataframe with extra `hex_id`, `num_records` and `color` columns.
        :raises `DFIInputValueError`: If `time_interval` or `polygon` are ill-formed.

        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)

        entity = "299eb59a-e47e-48c0-9ad5-89a9ce1303f4"
        polygon = [[-0.1169,51.5096], [-0.1184,51.5090], [-0.1167,51.5074], [-0.1153,51.5079], [-0.1169,51.5096]]
        start_time = datetime.strptime("2022-01-01T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
        end_time = datetime.strptime("2022-01-01T08:30:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),

        dfi.analyse.records_for_entity_id_with_heatmap_aggregation(
            entity_id=entity,
            h3_resolution=11,
            polygon=polygon,
            time_interval=(start_time,end_time),
        )
        ```
        """
        df_records = self.get.records(entities=[entity_id], polygon=polygon, time_interval=time_interval)

        if len(df_records) == 0:
            _logger.debug("No history found for entity %s", entity_id)
            return gpd.GeoDataFrame(
                columns=[
                    "entity_id",
                    "latitude",
                    "longitude",
                    "timestamp",
                    "hex_id",
                    "period_start",
                    "period end",
                ]
            )

        return self.add_heatmap_aggregation(df_records, h3_resolution=h3_resolution)


def _aggregate_records(df_input: pd.DataFrame, hex_id: str) -> pd.DataFrame:
    return (
        df_input.groupby(hex_id)
        .agg(
            num_records=("entity_id", "count"),
            num_devices=("entity_id", "nunique"),
            first_ping=("timestamp", "min"),
            last_ping=("timestamp", "max"),
        )
        .reset_index()
    )
