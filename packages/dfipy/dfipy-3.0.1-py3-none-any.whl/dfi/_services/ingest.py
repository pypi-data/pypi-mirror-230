"""
Class with DFI getters, wrappers of the DFI python API for ingest methods.
Composition of the class Connection.
"""
import logging
from typing import List, Optional, Union

from dfi import validate
from dfi.connect import Connect

_logger = logging.getLogger(__name__)


class Ingest:
    """
    Class responsible to call the HTTP API and ingest data into the DFI.

    It can be accessed via the a dfi.Client class instance or it must be instantiated
    with a dfi.Connect instance as argument.

    :param conn: Instance of a Connect with the credentials and namespace of the DFI connection.
    :example:
    ```python
    from dfi import Client

    dfi = Client(dfi_token, instance_name, namespace, base_url)
    dfi.ingest.from_file(file_to_spatiotemporal_data)
    ```
    """

    def __init__(self, conn: Connect) -> None:
        self.conn = conn

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def from_data(self, data: List[dict]) -> dict:
        """
        Insert data in an instance of a Data Flow Index, passed as a list of dicts, with coordinates.

        :param data: List of dict as in the example below.
        :raises `DFIInputDataError`: if the input dictionaries do not have the correct keys.
        :raises `DFIInputValueOutOfBoundError`: if the input coordinates are out of bound.
        :return: dict with a status message.
        :example:
        ```python
        from dfi import Client

        data = [
            {
                "coordinate": [-73.985664,40.748441],
                "time": "2022-09-01T17:32:28.250Z",
                "id": 0,
                "payload": "Application specific data"
            },
            {
                "coordinate": [-73.985645,40.748423],
                "time": "2022-09-01T17:32:40.310Z",
                "id": 1,
                "payload": "Application specific data"
            }
        ]

        dfi = Client(dfi_token, instance_name, namespace, base_url)

        dfi.insert.from_data(data)
        ```
        """
        validate.data(data)

        params = {"instance": self.conn.qualified_instance_name}

        with self.conn.api_post("insert", params=params, payload=data) as response:
            msg = f"Ingesting data. Response from DFI {response.text}"
            _logger.info(msg)
            result = response.json()
            result.update({"msg": msg})
            return result

    def from_s3(self, url_s3: Union[str, List[str]], data_format: Optional[dict] = None) -> dict:
        """
        Insert data in an instance of a Data Flow Index from a pre-signed URL, or a list of pre-signed URLs
        to an s3 bucket the user have access to, and can create pre-signed URLs.

        A pre-signed URL can be created from the AWS UI selecting a file from a bucket, then selecting "share with a presigned URL"
        under the "Action" drop-bar.

        :param url_s3: [str or list[str]] pre-signed S3 URL pointing to a file, or a list of pre-signed S3 URL pointing to files.
        :param data_format: Optional dict where the columns are specified. If None it will use the default:
            ```python
            data_format = {
                "columns":
                    {
                        "entityId": 0,
                        "timestamp": 1,
                        "longitude": 2,
                        "latitude": 3
                    }
                }
            ```
        :return: dict with a status message.
        :raises `DFIInputValueError`: if the input is not a string or a list of strings.
        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)
        data_format = {
            "columns":
                {
                    "entityId": 0,
                    "timestamp": 1,
                    "longitude": 2,
                    "latitude": 3
                }
            }
        dfi.insert.from_s3(<path to s3 bucket>, data_format=data_format)
        ```
        """
        validate.url_s3(url_s3)

        if data_format is None:
            data_format = {"columns": {"entityId": 0, "timestamp": 1, "longitude": 2, "latitude": 3}}

        urls = url_s3
        if isinstance(url_s3, str):
            urls = [urls]

        payload = {
            "source": {"urls": urls},
            "format": data_format,
        }
        with self.conn.api_put("import/batch", params=payload) as response:
            msg = f"Ingesting data from s3 URL {url_s3}. Response from DFI {response.text}"
            _logger.info(msg)
            result = response.json()
            result.update({"msg": msg})
            return result

    def check_s3_import_status(self, ingestion_id) -> dict:
        """
        Check the status of an ingestion via s3.

        :param ingestion_id: str with the ingestion id obtained as the output of self.from_s3.
        :return: dict with a status message and the count of entities inserted.
        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)
        dfi.insert.check_s3_import_status(<ingestion id>)
        ```
        """
        with self.conn.api_get(f"import/batch/{ingestion_id}/status") as response:
            msg = f"Status for ingestion {ingestion_id} request submitted. Response from DFI {response.text}"
            _logger.info(msg)
            result = response.json()
            result.update({"msg": msg})
            return result
