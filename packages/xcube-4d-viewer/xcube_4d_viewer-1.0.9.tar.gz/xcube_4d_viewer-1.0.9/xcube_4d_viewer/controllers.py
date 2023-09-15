"""Implements logic of the route handlers; xcube convention."""
from datetime import datetime
import math
from typing import Dict, Tuple

from matplotlib.colors import Normalize
import numpy as np
from numpy.typing import NDArray
from xarray import DataArray
from xarray import Dataset
from xcube.core._tile2 import get_var_valid_range
from xcube.core.mldataset import MultiLevelDataset
from xcube.core.timecoord import timestamp_to_iso_string

from xcube_4d_viewer.context import FourDContext
from xcube_4d_viewer.helpers.general_helpers import \
    variable_id_to_dataset_and_variable
from xcube_4d_viewer.helpers.image_functions import \
    convert_array_to_image_bytes
from xcube_4d_viewer.helpers.image_functions import pad_image_array
from xcube_4d_viewer.tile import Tile

VARIABLES = {}
VARIABLE_CONFIGS = {}

#  limit value ensures we still compute value ranges for our own data but not deepesdl (which is much larger)
COMPUTE_VALUE_RANGE_SIZE_LIMIT = 200000000


def get_variables(four_d_ctx: FourDContext) -> Dict:
    """
    Returns details of all variables that can be queried for tiles by the 4d viewer.

    For now, we only return variables inside .levels datasets - we let the levels determine available resolutions.

    We store the computed details within a global VARIABLES dictionary so that we do not have to recompute this for each
    call. Available datasets are determined by config.yml file passed to the server on start up, so we can assume that
    no new datasets will become available while the server is running. I believe we can also safely assume that the
    underlying dataset data will not be modified while the server is running - concurrent unprotected read/write.

    Parameters
    ----------
    four_d_ctx : FourDContext
        Context of API

    Returns
    -------
    Dict
        Dict with variable names as keys and variable detail dictionaries as values. The values are in a format expected
        by the middle tier service.
    """
    global VARIABLES

    if len(VARIABLES) > 0:
        return VARIABLES

    dataset_configs = four_d_ctx.datasets_ctx.get_dataset_configs()

    tmp_variables = {}
    for dataset_config in dataset_configs:
        if dataset_config['Path'].endswith('levels'):
            dataset_id = dataset_config['Identifier']
            ml_dataset = four_d_ctx.datasets_ctx.get_ml_dataset(ds_id=dataset_id)
            tile_size_x, tile_size_y = ml_dataset.grid_mapping.tile_size
            dataset_is_terrain_friendly = _is_power_of_two(tile_size_x - 1) and _is_power_of_two(tile_size_y - 1)

            for variable_name, variable in ml_dataset.base_dataset.data_vars.items():
                variable_name = str(variable_name)
                if len(variable.dims) < 2 \
                   or variable.dims[-2] not in ['y', 'lat'] \
                   or variable.dims[-1] not in ['x', 'lon']:
                    continue

                variable_id = f"{dataset_id}.{variable_name}"

                # if 'title' or 'long_name' defined in variable attributes, extract and use for frontend display
                # otherwise, just use the variable name we already have
                variable_nice_name = variable.attrs.get('title', variable.attrs.get('long_name', variable_name))

                # TODO: improve logic for determining ui-type
                variable_tile_type = 'heatmap3d' if 'z' in variable.dims \
                    else 'heightmap' if dataset_is_terrain_friendly \
                    else 'heatmap'

                # TODO: replace last-modified with actual value
                tmp_variables[variable_id] = {
                    'id': variable_id,
                    'last-modified': datetime(2023, 1, 1, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'name': variable_nice_name,
                    'ui-type': variable_tile_type,
                    'ui-path': f"/xcube/{dataset_id}/"}

    VARIABLES = tmp_variables
    return VARIABLES


def get_config_for_variable(four_d_ctx: FourDContext, variable_id: str) -> Dict:
    """
    Return configuration details for a specific variable.

    The return format matches convention expected by the middle tier service.

    We store the computed details within a global VARIABLE_CONFIG to avoid recomputing on each call - see
    get_variables() docstring for more details.

    Thanks to this, we can then retrieve and utilise the configuration when computing tiles. The key
    ['data-set']['ui-type'] is used to determine how to compute tile results (terrain/3D volume/heatmaps handled
    differently). The key ['data-set']['value-range'] is used to normalise the tile data. The latter is particularly
    useful to have precomputed, as determining value range sometimes requires loading in all of the dataset data.

    Additionally, we also utilise the global VARIABLES, as the details returned by  get_variables() and
    get_config_for_variable() have some keys in common (ui-type, last-modified, ui-path).

    In most cases (i.e. when used via the viewer) get_variables() will get called first, the get_config_for_variable(),
    and finally compute_tile(). This means that the global variables will already be computed when utilised elsewhere.

    Parameters
    ----------
    four_d_ctx : FourDContext
        Context of API
    variable_id : str
        Variable ID of the format <dataset_id>.<variable_name>

    Returns
    -------
    Dict
        Computed variable configuration, in format expected by the middle tier service
    """
    global VARIABLES, VARIABLE_CONFIGS

    if variable_id in VARIABLE_CONFIGS:
        return VARIABLE_CONFIGS[variable_id]

    dataset_id, variable_name = variable_id_to_dataset_and_variable(variable_id=variable_id)

    ml_dataset = four_d_ctx.datasets_ctx.get_ml_dataset(ds_id=dataset_id)
    base_dataset = ml_dataset.base_dataset
    variable = base_dataset[variable_name]

    variable_value_range = _get_variable_value_range(four_d_ctx, dataset_id, variable_name, variable)

    dataset_dict = get_variables(four_d_ctx)[variable_id]

    variable_config = {
        "data-set": {
            'units': variable.attrs.get('units', ''),
            'value-range': {"min": float(variable_value_range[0]),
                            "max": float(variable_value_range[1])},
            'times': [timestamp_to_iso_string(val) for val in variable.coords['time'].values] if 'time' in variable.dims
            else ["2010-01-01T00:00:00Z"],
            'last-modified': dataset_dict['last-modified'],
            'ui-type': dataset_dict['ui-type'],
            'ui-path': dataset_dict['ui-path']
        },
        "tile-grid": _compute_tile_grid(ml_dataset=ml_dataset,
                                        base_dataset=base_dataset,
                                        variable_type=dataset_dict['ui-type'])
    }
    VARIABLE_CONFIGS[variable_id] = variable_config
    return variable_config


def compute_tile(four_d_ctx: FourDContext, tile: Tile) -> bytes:
    ml_dataset = four_d_ctx.datasets_ctx.get_ml_dataset(ds_id=tile.dataset_id)

    assert tile.resolution_index <= ml_dataset.num_levels, \
        (f"Requested resolution index {tile.resolution_index} is outside of"
         + f"{tile.dataset_id} with {ml_dataset.num_levels} levels")

    # 4D viewer resolution_index 0 refers to lowest level of detail; the opposite is true for xcube dataset levels
    dataset_level = ml_dataset.num_levels - tile.resolution_index - 1

    variable_config = get_config_for_variable(four_d_ctx=four_d_ctx, variable_id=tile.variable_id)
    tile_size = variable_config['tile-grid']['tile-size']
    is_terrain = variable_config['data-set']['ui-type'] == 'heightmap'

    dataset_for_resolution = ml_dataset.get_dataset(dataset_level)
    variable = dataset_for_resolution[tile.variable_name]

    tile_data = retrieve_tile_data(ml_dataset, variable, tile, tile_size, dataset_level, is_terrain)

    tile_data = _normalise_data(tile_data, (variable_config['data-set']['value-range']['min'],
                                            variable_config['data-set']['value-range']['max']))

    desired_image_size = (tile_size['z'], tile_size['y'], tile_size['x']) if 'z' in tile_size \
        else (tile_size['y'], tile_size['x'])

    tile_data = pad_image_array(data=tile_data, new_dimension_sizes=desired_image_size, pad_value=np.nan)

    return convert_array_to_image_bytes(tile_data, variable_config['data-set']['ui-type'])


def _is_power_of_two(n) -> bool:
    return (n != 0) and (n & (n - 1) == 0)


def retrieve_tile_data(ml_dataset: MultiLevelDataset, variable: DataArray, tile: Tile, tile_size: Dict,
                       dataset_level: int, is_terrain: bool = False) -> NDArray:
    # for terrain, add one pixel of overlap between neighbouring tiles to ensure a surface with no gaps
    offset = -1 if is_terrain else 0

    x_start = (tile_size['x'] + offset) * tile.x
    y_start = (tile_size['y'] + offset) * tile.y

    ds_x_name, ds_y_name = ml_dataset.grid_mapping.xy_dim_names
    dim_selection = {ds_y_name: slice(y_start, y_start + tile_size['y']),
                     ds_x_name: slice(x_start, x_start + tile_size['x'])}

    if 'time' in variable.dims:
        dim_selection['time'] = tile.time_index

    if 'z' in tile_size:
        downscale_factor = 2 ** dataset_level
        z_start = (tile_size['z'] + offset) * tile.z * downscale_factor
        z_end = z_start + tile_size['z'] * downscale_factor
        indices = [i for i in range(z_start, z_end, downscale_factor) if i < variable.shape[variable.dims.index('z')]]
        dim_selection['z'] = indices

    return variable.isel(dim_selection)


def _normalise_data(data_array: NDArray, value_range: Tuple[float, float]) -> NDArray:
    value_min, value_max = value_range

    if math.isclose(value_min, value_max):
        value_max = value_min + 1
    norm = Normalize(
        value_min, value_max, clip=True
    )
    return norm(data_array)


def _get_variable_value_range(
        four_d_ctx: FourDContext, dataset_id: str, variable_name: str, variable: DataArray) -> Tuple[float, float]:
    """
    Compute value range of variable.

    First, we try to retrieve color mapping value range set in the xcube server config and return if found.

    Then, we check the xarray variable for a 'valid_range' attribute and return if found.

    Finally, if neither of the above is defined, compute range from actual data within the variable if the variable
    size is below our defined limit. Otherwise, return the default range (0., 1.).

    Parameters
    ----------
    four_d_ctx : FourDContext
        Context of API
    dataset_id : str
        ID of dataset for variable
    variable_name : str
        Name of variable
    variable : DataArray
        Variable DataArray retrieved from the dataset instance

    Returns
    -------
    Tuple[float, float]
        Computed variable range
    """
    color_mappings = four_d_ctx.datasets_ctx.get_color_mappings(dataset_id)
    if color_mappings:
        color_mapping = color_mappings.get(variable_name)
        if color_mapping:
            valid_range = color_mapping.get('ValueRange', (None, None))

            if None not in valid_range:
                return valid_range

    valid_range = get_var_valid_range(variable)

    if valid_range is not None:
        return valid_range

    #  return default limit if variable is too large to compute the value range
    #  TODO: need a better way of handling this. Currently, normalisation/colour ramps will be affected - normalised
    #  just on per-tile basis. If we decide that it is just up to the user to define their valid min/max in data cube
    #  attributes or xcube serve config.yml, we should perhaps at least display a warning if these are not defined
    #  *and* we are unable to compute the actual value range ourselves.
    if variable.size <= COMPUTE_VALUE_RANGE_SIZE_LIMIT:
        return (np.nanmin(variable[:]), np.nanmax(variable[:]))
    else:
        return (0., 1.)


def _compute_tile_grid(ml_dataset: MultiLevelDataset, base_dataset: Dataset, variable_type: str) -> Dict:
    ds_x_name, ds_y_name = ml_dataset.grid_mapping.xy_dim_names
    is_terrain = variable_type == 'heightmap'
    base_tile_grid = {
        "extent": {
            "x": {"min": base_dataset.coords[ds_x_name].values.min(),
                  "max": base_dataset.coords[ds_x_name].values.max()},
            "y": {"min": base_dataset.coords[ds_y_name].values.min(),
                  "max": base_dataset.coords[ds_y_name].values.max()}, },
        "tile-size": {
            "x": ml_dataset.grid_mapping.tile_size[0],
            "y": ml_dataset.grid_mapping.tile_size[1]},
        "lowest-resolution-tile-extent": {
            "x": _calculate_lowest_resolution_extent(tile_size=ml_dataset.grid_mapping.tile_size[0],
                                                     is_terrain=is_terrain,
                                                     highest_resolution=ml_dataset.resolutions[0][0],
                                                     number_of_resolutions=ml_dataset.num_levels),
            'y': _calculate_lowest_resolution_extent(tile_size=ml_dataset.grid_mapping.tile_size[1],
                                                     is_terrain=is_terrain,
                                                     highest_resolution=ml_dataset.resolutions[0][1],
                                                     number_of_resolutions=ml_dataset.num_levels)},
        "tile-orientation": {
            "x": "positive",
            "y": "negative"},
        "number-of-resolutions": ml_dataset.num_levels
    }

    base_tile_grid['origin'] = {'x': base_tile_grid['extent']['x']['min'],
                                'y': base_tile_grid['extent']['y']['max']}

    if variable_type == 'heatmap3d':
        base_tile_grid['extent']['z'] = {'min': base_dataset.coords['z'].values.min(),
                                         'max': base_dataset.coords['z'].values.max()}
        base_tile_grid['origin']['z'] = base_tile_grid['extent']['z']['min']
        base_tile_grid['tile-size']['z'] = base_dataset.chunksizes['z'][0]
        base_tile_grid['tile-orientation']['z'] = 'positive'

        max_z_resolution = ((base_tile_grid['extent']['z']['max'] - base_tile_grid['extent']['z']['min'])
                            / base_dataset.dims['z'])
        base_tile_grid['lowest-resolution-tile-extent']['z'] = _calculate_lowest_resolution_extent(
            tile_size=base_tile_grid['tile-size']['z'],
            is_terrain=is_terrain,
            highest_resolution=max_z_resolution,
            number_of_resolutions=ml_dataset.num_levels)

    return base_tile_grid


def _calculate_lowest_resolution_extent(tile_size: float, is_terrain: bool, highest_resolution: float,
                                        number_of_resolutions: float) -> float:

    # Tiles of a fixed number of pixels that represent vertices do not cover the same spatial exent as equivalent
    # raster pixels.
    pixel_adjustment = -1 if is_terrain else 0

    return float((tile_size + pixel_adjustment) * highest_resolution * 2**(number_of_resolutions - 1))
