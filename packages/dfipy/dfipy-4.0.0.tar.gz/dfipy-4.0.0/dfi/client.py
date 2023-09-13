"""
Class composition of all the other classes, to access the
wrappers with syntactic sugar.
"""
from dfi.connect import Connect
from dfi.services.delete import Delete
from dfi.services.get import Get
from dfi.services.info import Info
from dfi.services.ingest import Ingest
from dfi.services.polygons import Polygons


class Client:
    """
    Client class gathering all the classes and method in a single one. Facade of dfi.Connect.

    See documentation of dfi.Connect for its input values.

    :example:
    ```python
    from dfi import Client

    dfi = Client(dfi_token, instance_name, namespace, base_url)
    ```
    """

    def __init__(
        self,
        api_token: str,
        instance_name: str,
        namespace: str = None,
        base_url: str = None,
        query_timeout: int = 60,
        progress_bar: bool = False,
    ) -> None:
        self.conn = Connect(
            api_token=api_token,
            instance_name=instance_name,
            namespace=namespace,
            base_url=base_url,
            query_timeout=query_timeout,
            progress_bar=progress_bar,
        )
        self.delete = Delete(self.conn)
        self.get = Get(self.conn)
        self.info = Info(self.conn)
        self.ingest = Ingest(self.conn)
        self.polygons = Polygons(self.conn)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""
