"""Implements access to API resources; xcube convention."""
from __future__ import annotations

from xcube.server.api import ApiContext
from xcube.server.api import Context
from xcube.webapi.datasets.context import DatasetsContext


class FourDContext(ApiContext):

    def __init__(self, server_ctx: Context):
        super().__init__(server_ctx)
        self._datasets_ctx = server_ctx.get_api_ctx("datasets")

    @property
    def datasets_ctx(self) -> DatasetsContext:
        return self._datasets_ctx

    def get_middle_tier_url(self: FourDContext):
        return self.config.get('MiddleTierURL')

    def get_server_external_url(self: FourDContext):
        return self.config.get('ServerExternalURL')
