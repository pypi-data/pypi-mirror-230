"""Handles registration of the server with the middle tier service. Called on start/stop of the xcube server."""
import json
from posixpath import join as url_join
from uuid import uuid4

import requests
from xcube.server.server import ServerContext

data_source_id = f"xcube_{uuid4()}"

# save globally due to on_stop bug - when we manually call the deregister function, we do not have access to server_ctx
# but know this will have already been populated on_start
middle_tier_url = None


def register_server_with_middle_tier(server_ctx: ServerContext) -> None:
    """
    Register current server with the middle tier service.

    We pass an externally-accessible URL of the xcube server, which the middle tier adds to its list of sources. This
    allows the server to be queried by the 4D viewer.

    This method is called on start-up of the 4D viewer xcube API.

    Parameters
    ----------
    server_ctx : ServerContext
        xcube server context - contains address/port information.
    """
    global middle_tier_url
    middle_tier_url = server_ctx.get_api_ctx("4d-viewer").get_middle_tier_url()
    server_external_url = server_ctx.get_api_ctx("4d-viewer").get_server_external_url()

    server_external_url = url_join(server_external_url, '4d_viewer')

    response = requests.post(url=f"{middle_tier_url}/register-data-source/{data_source_id}",
                             data=json.dumps({"data_source_type": "xcube_server_data_source",
                                              "server_url": server_external_url}))
    if not response.ok:
        raise ConnectionError(f"failed to register with 4d_viewer middle tier service at {middle_tier_url}")


def deregister_server_with_middle_tier(server_ctx: ServerContext) -> None:
    """
    Deregister this server as a source within the middle tier service.

    Once called, the server is removed from middle tier's list of sources.

    Parameters
    ----------
    server_ctx : ServerContext
        xcube server context
    """
    global middle_tier_url

    if server_ctx is not None:
        middle_tier_url = server_ctx.get_api_ctx("4d-viewer").get_middle_tier_url()

    response = requests.delete(url=f"{middle_tier_url}/deregister-data-source/{data_source_id}")

    assert response.ok
    if server_ctx is None:
        # function called manually instead of via xcube server's on_stop. For some reason need to exit - hangs otherwise
        exit(0)
