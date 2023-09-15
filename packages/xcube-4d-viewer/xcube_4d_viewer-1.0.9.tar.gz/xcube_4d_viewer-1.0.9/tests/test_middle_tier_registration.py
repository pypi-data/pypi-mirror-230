"""Testing the registration module."""
import json
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from xcube_4d_viewer.middle_tier_registration import data_source_id
from xcube_4d_viewer.middle_tier_registration import \
    deregister_server_with_middle_tier
from xcube_4d_viewer.middle_tier_registration import \
    register_server_with_middle_tier


@pytest.fixture()
def mock_server_ctx():
    mock_4d_viewer_ctx = MagicMock()
    mock_4d_viewer_ctx.get_middle_tier_url.return_value = 'http://dummy-url'
    mock_4d_viewer_ctx.get_server_external_url.return_value = 'http://dummy-server-url'

    mock_server_ctx = MagicMock()
    mock_server_ctx.get_api_ctx.return_value = mock_4d_viewer_ctx
    return mock_server_ctx


def test_register_server_with_middle_tier(mock_server_ctx):
    with patch("xcube_4d_viewer.middle_tier_registration.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.ok = True
        mock_post.return_value = mock_response
        register_server_with_middle_tier(mock_server_ctx)
        mock_post.assert_called_once_with(url=f"http://dummy-url/register-data-source/{data_source_id}",
                                          data=json.dumps({"data_source_type": "xcube_server_data_source",
                                                           "server_url": "http://dummy-server-url/4d_viewer"}))


def test_deregister_server_with_middle_tier(mock_server_ctx):
    with patch("xcube_4d_viewer.middle_tier_registration.requests.delete") as mock_delete:
        mock_response = MagicMock()
        mock_response.ok = True
        mock_delete.return_value = mock_response
        deregister_server_with_middle_tier(mock_server_ctx)
        mock_delete.assert_called_once_with(url=f"http://dummy-url/deregister-data-source/{data_source_id}")
