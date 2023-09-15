"""Registers our plugin package with xcube; xcube convention."""
from xcube.constants import EXTENSION_POINT_SERVER_APIS
from xcube.util.extension import ExtensionRegistry
from xcube.util.extension import import_component


def init_plugin(ext_registry: ExtensionRegistry):
    ext_registry.add_extension(
        loader=import_component("xcube_4d_viewer.api:api"),
        point=EXTENSION_POINT_SERVER_APIS,
        name="Earthwave 4D Viewer API"
    )
