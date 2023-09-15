"""Defines routes of the 4D viewer xcube API."""
from xcube.server.api import ApiHandler

from xcube_4d_viewer.api import api
from xcube_4d_viewer.context import FourDContext
from xcube_4d_viewer.controllers import compute_tile
from xcube_4d_viewer.controllers import get_config_for_variable
from xcube_4d_viewer.controllers import get_variables
from xcube_4d_viewer.route_parameters import PATH_PARAM_EXT
from xcube_4d_viewer.route_parameters import PATH_PARAM_RESOLUTION
from xcube_4d_viewer.route_parameters import PATH_PARAM_TIME
from xcube_4d_viewer.route_parameters import PATH_PARAM_VAR_ID
from xcube_4d_viewer.route_parameters import PATH_PARAM_X
from xcube_4d_viewer.route_parameters import PATH_PARAM_Y
from xcube_4d_viewer.route_parameters import PATH_PARAM_Z
from xcube_4d_viewer.tile import Tile


@api.route("/4d_viewer/variables")
class VariableHandler(ApiHandler[FourDContext]):

    @api.operation(operation_id="getVariables",
                   summary="Get available variables.")
    async def get(self):
        variable_dicts = get_variables(four_d_ctx=self.ctx)
        self.response.finish({"variables": list(variable_dicts.values())})


@api.route("/4d_viewer/{variable_id}/configuration")
class VariableConfigurationHandler(ApiHandler[FourDContext]):

    @api.operation(operation_id="getVariableConfig",
                   summary="Get config for variable.",
                   parameters=[PATH_PARAM_VAR_ID])
    async def get(self, variable_id: str):
        config = get_config_for_variable(four_d_ctx=self.ctx, variable_id=variable_id)

        self.response.finish(config)


@api.route("/4d_viewer/{variable_id}/tiles/{resolution_index}/{x}_{y}_{z}_{time_index}_{extension}")
class FourDTileHandler(ApiHandler[FourDContext]):

    @api.operation(operation_id="getFourDTile",
                   summary="Get a tile for the 4D Viewer.",
                   parameters=[PATH_PARAM_VAR_ID,
                               PATH_PARAM_TIME,
                               PATH_PARAM_RESOLUTION,
                               PATH_PARAM_X,
                               PATH_PARAM_Y,
                               PATH_PARAM_Z,
                               PATH_PARAM_EXT])
    async def get(self, variable_id, resolution_index, time_index, extension, x, y, z):

        tile_definition = Tile(variable_id=variable_id,
                               resolution_index=int(resolution_index),
                               time_index=int(time_index),
                               x=int(x),
                               y=int(y),
                               z=int(z) if z != "None" else None,
                               extension=extension)

        computed_tile = await self.ctx.run_in_executor(
            None,
            compute_tile,
            self.ctx,
            tile_definition
        )
        if extension == "png":
            self.response.set_header('Content-Type', 'image/png')
        else:
            self.response.set_header('Content-Type', 'application/octet-stream')
        await self.response.finish(computed_tile)
