"""
Storage and retrieval of named polygons in the DFI Web API.
"""

import logging
from typing import List, Tuple

from dfi import validate
from dfi.connect import Connect
from dfi.models import Polygon

_logger = logging.getLogger(__name__)


class Polygons:
    """
    Class responsible to call the DFI API and access the polygons DB.

    The polygon DB is a dataset of named polygons. It is made available to the user within the same
    namespace of where the DFI instances lives.

    It can be accessed via the a dfi.Client class instance or it must be instantiated
    with a dfi.Connect instance as argument.

    :param dfi_conn: Instance of a Connect with the credentials and namespace of the DFI connection.

    :example:
    ```python
    from dfi import Client

    dfi = Client(dfi_token, instance_name, namespace, base_url)

    dfi_polygons.get_vertices("my polygon name")
    ```
    """

    def __init__(self, dfi_conn: Connect) -> None:
        self.conn: Connect = dfi_conn

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def get_names(self) -> List[dict]:
        """
        Retrieves a list of saved polygons.

        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)

        dfi.polygons.get_names()
        ```
        """
        with self.conn.api_get("polygons") as response:
            list_polygons = response.json().get("polygons")
            validate.list_polygons_response(list_polygons, response)
            return list_polygons

    def get_vertices(self, polygon_name: str) -> List[List[float]]:
        """
        Get the list of a polygon saved in the polygon database from its name.

        :param polygon_name: Name of the polygon the user wants to retrieve from the polygons database.
        :returns: List of the polygon coordinates.
        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)

        dfi.polygons.get_names()
        dfi.polygons.get_vertices('my-first-polygon')
        ```
        """
        validate.polygon_name(polygon_name)
        with self.conn.api_get("polygons/" + polygon_name) as response:
            vertices = response.json().get("vertices")
            validate.vertices_response(vertices, response)
            return vertices

    def get(self, polygon_name: str) -> dict:
        """
        Get the polygon json as it is stored in the DFI.
        To get only the vertices, please call self.get_vertices(polygon_name)

        :param polygon_name: Name of the polygon the user wants to retrieve from the polygons database.
        :returns: json dictionary of the saved polygon.
        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)

        dfi.polygons.get_names()
        dfi.polygons.get('my-first-polygon')
        ```
        """
        validate.polygon_name(polygon_name)
        with self.conn.api_get("polygons/" + polygon_name) as response:
            return response.json()

    def save(self, polygon_name: str, polygon: Polygon, is_public: bool = False) -> str:
        """
        Save a polygon to the DFI.

        :param polygon_name: Name of the polygon the user wants to save to database. It must not contain spaces.
        :param polygon: List of vertices [[lon1, lat1], [lon2, lat2], ...] or a list of four
            floats representing the bounding box extremes as [lon_min, lat_min, lon_max, lat_max].
            Non valid input will raise an error.
        :param is_public: other users can access the polygon, prefixing it with the namespace where the polygon is created.
            False by default. It can be true only if the user is associated with a default namespace. If the user is
            not associated to a namespace, the method will fail.
        :return: string with a status message.
        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)
        region = [
            [25.774, -80.19],
            [18.466, -66.118],
            [32.321, -64.757],
            [25.774, -80.19],
        ]

        dfi.polygons.save("my-first-polygon", region)
        ```
        """
        validate.polygon_name(polygon_name)
        if is_public is True:
            _logger.info(
                "You are creating a public polygon. "
                "If no namespace is associated to your user the POST method will fail."
            )
        validate.polygon(polygon)

        if isinstance(polygon[0], float):
            polygon = from_bbox_to_polygon_list(polygon)

        payload = {
            "name": polygon_name,
            "public": is_public,
            "vertices": polygon,
        }
        with self.conn.api_post(endpoint="polygons", stream=True, payload=payload) as response:
            msg = f"Polygon {polygon_name} added to database. Response from DFI: {response.text}."
            _logger.info(msg)
            return msg

    def delete(self, polygon_name) -> str:
        """
        Delete a polygon from the database by name.

        :param polygon_name: Name of the polygon the user wants to save to database. It must not contain spaces.
        :return: string with a status message.
        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)
        dfi.polygons.delete("my-first-polygon")
        ```
        """
        validate.polygon_name(polygon_name)
        with self.conn.api_delete(f"polygons/{polygon_name}") as response:
            msg = f"Delete request for {polygon_name} submitted. Response from DFI {response.text}"
            _logger.info(msg)
            return msg

    def set_public_state(self, polygon_name: str, is_public: bool) -> str:
        """
        Changes the 'share' status for the given polygon.

        You can get the state of a current polygon with `dfi.polygons.get_public_state(<polygon name>)` method.

        :param polygon_name: Name of the polygon the user wants to save to database. It must not contain spaces.
        :param is_public: other users can access the polygon, prefixing it with the namespace where the polygon is created.
            It can be true only if the user is associated with a default namespace. If the user is not associated to
            a namespace, the method will fail. You can check your user's details with `dfi.info.profile()` method.
        :return: string with a status message.
        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)
        dfi.polygons.set_public_state("my-first-polygon", is_public=True)
        ```
        """
        validate.polygon_name(polygon_name)
        with self.conn.api_put(f"polygons/{polygon_name}", data={"public": is_public}) as response:
            msg = f"Public state set to {is_public} for {polygon_name}. Response from DFI {response.text}"
            _logger.info(msg)
            return msg

    def get_public_state(self, polygon_name: str) -> bool:
        """
        Get the shared status (True/False) of a polygon saved in the polygon database from its name.

        :param polygon_name: Name of the polygon the user wants to retrieve from the polygons database.
        :returns: boolean with the shared state of the selected polygon.
        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)

        dfi.polygons.get_names()
        dfi.polygons.get_shared_state('my-first-polygon')
        ```
        """
        validate.polygon_name(polygon_name)
        with self.conn.api_get(f"polygons/{polygon_name}") as response:
            return response.json().get("public")


def from_bbox_to_polygon_list(bounding_box: List[float]) -> Tuple[Tuple[float, float]]:
    """Convert a bounding box, passed as a list `[min_lon, min_lat, max_lon, max_lat]` into a tuple of vertices."""
    validate.bounding_box(bounding_box)
    min_lon, min_lat, max_lon, max_lat = bounding_box
    return ((max_lon, max_lat), (max_lon, min_lat), (min_lon, min_lat), (min_lon, max_lat), (max_lon, max_lat))
