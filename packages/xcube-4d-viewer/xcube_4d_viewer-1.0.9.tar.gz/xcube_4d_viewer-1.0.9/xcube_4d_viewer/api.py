"""Defines the API object; xcube convention."""
import signal

from xcube.server.api import Api
from xcube.util.jsonschema import JsonObjectSchema
from xcube.webapi.common.schemas import URI_SCHEMA

from xcube_4d_viewer.context import FourDContext
from xcube_4d_viewer.middle_tier_registration import \
    deregister_server_with_middle_tier
from xcube_4d_viewer.middle_tier_registration import \
    register_server_with_middle_tier


def sig_handler(_sig, _frame):
    deregister_server_with_middle_tier(None)


api = Api("4d-viewer",
          create_ctx=FourDContext,
          required_apis=["datasets"],
          description="4D Viewer by Earthwave",
          on_start=register_server_with_middle_tier,
          on_stop=deregister_server_with_middle_tier,
          config_schema=JsonObjectSchema(
              properties={'MiddleTierURL': URI_SCHEMA,
                          'ServerExternalURL': URI_SCHEMA},
              required=['MiddleTierURL', 'ServerExternalURL']
          ))

# call deregister_server_with_middle_tier on exit. Temporary hack - necessary due to the on_stop above not working
signal.signal(signal.SIGINT, sig_handler)
