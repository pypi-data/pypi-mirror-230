"""
Class with DFI getters, wrappers of the DFI python API for ingest methods.
Composition of the class Connection.
"""
import logging

from dfi.connect import Connect

_logger = logging.getLogger(__name__)


class Delete:
    """
    Class responsible to call the HTTP API and delete data from DFI.

    It can be accessed via the a dfi.Client class instance or it must be instantiated
    with a dfi.Connect instance as argument.

    :param conn: Instance of a Connect with the credentials and namespace of the DFI connection.
    :example:
    ```python
    from dfi import Client

    dfi = Client(dfi_token, instance_name, namespace, base_url)
    dfi.delete.by_instance(instance_name)
    ```
    """

    def __init__(self, conn: Connect) -> None:
        self.conn = conn

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def by_instance(self, instance_name: str) -> dict:
        """
        Delete all data in the target DFI instance.

        :param instance_name: str with the DFI instance to delete.
            Note: it is not possible to delete data from a dfi instance you have no permission,
            or that you have not created.
        :return: dict with a status message and the ingestion id (see Ingest.check_s3_import_status).
        :example:
        ```python
        from dfi import Client

        dfi = Client(dfi_token, instance_name, namespace, base_url)
        dfi.delete.by_instance(instance_name)
        ```
        """
        with self.conn.api_post(f"instances/{instance_name}/truncate") as response:
            msg = f"Truncating instance {instance_name}. Response from DFI {response.text}"
            _logger.info(msg)
            result = response.json()
            result.update({"msg": msg})
            return result
