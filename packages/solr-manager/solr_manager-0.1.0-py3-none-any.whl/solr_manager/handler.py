from solr_manager.client import SolrClient


class BaseHandler:
    def __init__(self, client: SolrClient = None) -> None:
        if client is None:
            raise Exception("client is required")

        self.client = client
