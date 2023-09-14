"""This is a generated file, you should not change it!"""

from typing import Any, List, Mapping

from solr_manager.handler import BaseHandler
from solr_manager.response import SolrResponse


class UpdateAPI(BaseHandler):
    def update(
        self,
        collection: str,
        data: List[Mapping[str, Any]],
        commit=False,
    ) -> SolrResponse:
        path = f"solr/{collection}/update?commit={str(commit).lower()}"

        return self.client.post(
            path,
            json=data,
            headers={"Content-Type": "application/json"},
        )
