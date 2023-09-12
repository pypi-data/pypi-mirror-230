"""
Class composition of all the other classes, to access the
wrappers with syntactic sugar.
"""
import json
import subprocess
import warnings
from typing import List

from dfi._services.delete import Delete
from dfi._services.get import Get
from dfi._services.info import Info
from dfi._services.ingest import Ingest
from dfi._services.polygons import Polygons
from dfi.connect import Connect


def get_extra_installed() -> List[str]:
    """Check if the library was installed with extra functionalities"""
    try:
        inspect = subprocess.run(["pip", "inspect"], capture_output=True, text=False, check=False, encoding="utf-8")
        dict_inspect = json.loads(inspect.stdout)
        dict_inspect = {v["metadata"]["name"]: v["metadata"] for v in dict_inspect["installed"]}
        return dict_inspect["dfipy"]["provides_extra"]

    except subprocess.CalledProcessError as err:
        raise EnvironmentError(
            f"We could not run 'pip inspect' on the given python environment. Subprocess returned {err}"
        ) from err

    except KeyError as err:
        warnings.warn(
            f"{err} `pip inspect` returned a python dictionary with non existing keys."
            "Extra methods will **not** be installed."
        )

    except json.decoder.JSONDecodeError as err:
        warnings.warn(
            f"There was a failure reading installed libraries.\n{err}\nExtra methods will **not** be installed."
        )
    return []


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

        self._extra_installed = get_extra_installed()

        if "analyse" in self._extra_installed or "complete" in self._extra_installed:
            from dfi._services.analyse import Analyse

            self.analyse = Analyse(self.conn)
        if "show" in self._extra_installed or "complete" in self._extra_installed:
            from dfi._services.show import Show

            self.show = Show(self.conn)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""
