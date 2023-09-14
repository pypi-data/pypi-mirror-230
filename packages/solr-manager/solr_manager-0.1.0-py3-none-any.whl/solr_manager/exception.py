from solr_manager.response import SolrResponse


class SolrException(Exception):
    def __init__(self, response: SolrResponse):
        super().__init__(response.error.msg)

        self.code = response.error.code
        self.metadata = response.error.metadata
        self.response = response
