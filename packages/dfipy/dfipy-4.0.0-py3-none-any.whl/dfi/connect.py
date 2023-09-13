"""
Class to connect to the DFI server.
"""
import logging
from typing import Optional

import requests

from dfi import validate

_logger = logging.getLogger(__name__)


class Connect:
    """
    Class instantiating the connectors to the DFI API.

    :param api_token: token provided by generalsystem.com to access the running DFI environments.
    :param instance_name: Name of a DFI API engine instance, living in the specified namespace.
    :param namespace: Name for the collection of instances of DFI engines where to find the specific instance to connect to.
    :param base_url: Base url where the service is located
    :param query_timeout: Time after an unresponsive query will be dropped.
    :param progress_bar: Visualise a progress bar if True (slows down the execution, typically used for demos and tests).

    :example:
    ````python
    dfi_conn = dfi.Connect(api_token, instance_name, namespace, base_url)

    dfi_conn.streaming_headers
    ````
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
        self.api_token = api_token
        self.base_url = base_url
        self.query_timeout = query_timeout
        self.streaming_headers = {
            "Authorization": f"Bearer {api_token}",
            "accept": "text/event-stream",
        }
        self.synchronous_headers = {
            "Authorization": f"Bearer {api_token}",
            "accept": "application/json",
            "content-type": "application/json",
        }
        self.namespace = namespace
        self.instance_name = instance_name
        self.progress_bar = progress_bar
        if namespace is None:
            self.qualified_instance_name = instance_name
        else:
            self.qualified_instance_name = f"{namespace}.{instance_name}"

    # The representation will expose the secret token
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.base_url}"

    def __str__(self) -> str:
        return f"""
                API connection instance
                base_url={self.base_url},
                namespace={self.namespace},
                instance_name={self.instance_name}
                """

    # get and post API wrappers
    def api_get(
        self,
        endpoint: str,
        stream: bool = True,
        params: Optional[dict] = None,
    ) -> requests.models.Response:
        """Helper wrapping requests.get method"""
        headers = self.streaming_headers
        url = f"{self.base_url}/{endpoint}"
        _logger.debug(dict(url=url, headers=headers, stream=stream, params=params, timeout=self.query_timeout))
        response = requests.get(
            url,
            headers=headers,
            stream=stream,
            params=params,
            timeout=self.query_timeout,
        )
        validate.response(response, url, headers, params)
        return response

    def api_post(
        self,
        endpoint: str,
        stream: bool = True,
        params: Optional[dict] = None,
        payload: Optional[dict] = None,
    ) -> requests.models.Response:
        """Helper wrapping requests.post method"""
        headers = self.streaming_headers
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            stream=stream,
            params=params,
            timeout=self.query_timeout,
        )
        validate.response(response, url, headers, params)
        return response

    def api_put(
        self,
        endpoint: str,
        stream: bool = True,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> requests.models.Response:
        """Helper wrapping requests.put method"""
        headers = self.streaming_headers
        url = f"{self.base_url}/{endpoint}"
        response = requests.put(
            url,
            headers=headers,
            data=data,
            stream=stream,
            params=params,
            timeout=self.query_timeout,
        )
        validate.response(response, url, headers, params)
        return response

    def api_delete(
        self,
        endpoint: str,
        stream: bool = True,
        params: Optional[dict] = None,
        payload: Optional[dict] = None,
    ) -> requests.models.Response:
        """Helper wrapping requests.delete method"""
        headers = self.streaming_headers
        url = f"{self.base_url}/{endpoint}"
        response = requests.delete(
            url,
            headers=headers,
            json=payload,
            stream=stream,
            params=params,
            timeout=self.query_timeout,
        )
        validate.response(response, url, headers, params)
        return response
