from typing import Optional, Tuple

import requests

from solr_manager.exception import SolrException
from solr_manager.parameters import parse_params
from solr_manager.response import SolrResponse


class SolrClient:
    def __init__(self, url: str, auth: Optional[Tuple[str, str]] = None):
        self.url = url
        self.auth = auth

    def request(
        self,
        method: str,
        path: str,
        *,
        json=None,
        params={},
        cookies=None,
        **kwargs,
    ) -> SolrResponse:
        url = f"{self.url}/{path}"

        raw = requests.request(
            method,
            url,
            json=json,
            auth=self.auth,
            params=parse_params(params),
            cookies=cookies,
            **kwargs,
        )

        raw.raise_for_status()

        response = SolrResponse(raw.json())

        if response.header.status != 0:
            raise SolrException(response)

        return response

    def get(self, path: str, **kwargs) -> SolrResponse:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> SolrResponse:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> SolrResponse:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> SolrResponse:
        return self.request("DELETE", path, **kwargs)

    def head(self, path: str, **kwargs) -> SolrResponse:
        return self.request("HEAD", path, **kwargs)
