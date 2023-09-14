# WIP

from solr_manager.client import SolrClient


class Stub:
    def __init__(self, client: SolrClient) -> None:
        self.client = client


class ApiStub(Stub):
    def create_route(self, route: str) -> None:
        self.client.request("POST", route)


class AdminStub(Stub):
    api: ApiStub


admin = AdminStub

admin.api.create_route("/solr/admin/collections")
