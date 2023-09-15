"""Testing the controllers module."""
from datetime import datetime
from datetime import timezone
from typing import Dict
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from xarray import DataArray
from xarray import Dataset
from xarray import Variable
from xcube.core.gridmapping.base import GridMapping
from xcube.core.mldataset import MultiLevelDataset
from xcube.webapi.datasets.context import DatasetsContext

from xcube_4d_viewer.context import FourDContext
from xcube_4d_viewer.controllers import get_config_for_variable
from xcube_4d_viewer.controllers import get_variables
from xcube_4d_viewer.tile import Tile


@pytest.fixture()
def mock_dataset():
    mock_dataset = MagicMock(spec=Dataset)
    mock_variable = MagicMock(spec=Variable)
    mock_variable.dims = ["time", "y", "x"]
    mock_variable.attrs = {'title': "Beautiful Variable",
                           'units': 'm'}
    time_xarray_mock = MagicMock(spec=DataArray)
    time_xarray_mock.values = [datetime(2020, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)]
    mock_variable.coords = {"time": time_xarray_mock}
    mock_dataset.__getitem__.return_value = mock_variable
    mock_dataset.data_vars = {'mock_variable': mock_variable}
    return mock_dataset


@pytest.fixture()
def mock_grid_mapping():
    mock_grid_mapping = MagicMock(spec=GridMapping)
    mock_grid_mapping.xy_bbox = [0, 1, 2, 3]
    mock_grid_mapping.tile_size = (256, 256)
    mock_grid_mapping.resolutions = [(0.025, 0.025), (0.5, 0.5), (0.1, 0.1)]
    return mock_grid_mapping


@pytest.fixture()
def mock_ml_dataset(mock_dataset: MagicMock, mock_grid_mapping: MagicMock):
    mock_ml_dataset = MagicMock(spec=MultiLevelDataset)
    mock_ml_dataset.base_dataset = mock_dataset
    mock_ml_dataset.get_dataset.return_value = mock_dataset
    mock_ml_dataset.grid_mapping = mock_grid_mapping
    mock_ml_dataset.resolutions = [(0.025, 0.025), (0.5, 0.5), (0.1, 0.1)]
    mock_ml_dataset.num_levels = 3
    return mock_ml_dataset


@pytest.fixture()
def mock_four_d_context():
    mock_four_d_context = MagicMock(spec=FourDContext)
    mock_datasets_context = MagicMock(spec=DatasetsContext)
    mock_four_d_context.dataset_ctx = mock_datasets_context
    return mock_four_d_context


@pytest.fixture()
def example_tile():
    return Tile(variable_id="mock_dataset.mock_variable",
                resolution_index=0,
                time_index=0,
                x=0,
                y=1,
                extension="png")


@pytest.fixture()
def example_variable_config() -> dict:
    return {
        'data-set':
            {'units': 'm',
             'value-range': {'min': 0.0, 'max': 1.0},
             'times': ['2020-01-01T00:00:00+00:00Z'],
             'ui-path': '/xcube/mock_dataset/',
             'ui-type': 'heatmap',
             'last-modified': '2023-01-01T00:00:00Z'},
        'tile-grid':
            {'extent': {'x': {'min': 0, 'max': 2},
                        'y': {'min': 1, 'max': 3}},
             'origin': {'x': 0, 'y': 3},
             'tile-size': {'x': 256, 'y': 256},
             'lowest-resolution-tile-extent': {'x': 25.6, 'y': 25.6},
             'tile-orientation': {'x': 'positive', 'y': 'negative'},
             'number-of-resolutions': 3}}


@pytest.fixture()
def example_variable_dict() -> Dict:
    return {'id': 'mock_dataset.mock_variable',
            'ui-path': '/xcube/mock_dataset/',
            'ui-type': 'heatmap',
            'last-modified': '2023-01-01T00:00:00Z',
            'name': 'Beautiful Variable'}


def test_get_variables(mock_four_d_context: MagicMock, mock_ml_dataset: MagicMock, example_variable_dict: Dict):

    mock_four_d_context.datasets_ctx.get_dataset_configs.return_value = [{"Identifier": "mock_dataset",
                                                                          "Path": "mock_dataset.levels"}]
    mock_four_d_context.datasets_ctx.get_ml_dataset.return_value = mock_ml_dataset

    variables = get_variables(four_d_ctx=mock_four_d_context)

    assert variables['mock_dataset.mock_variable'] == example_variable_dict


def test_get_config_for_variable(
        mock_four_d_context: MagicMock, mock_ml_dataset: MagicMock, example_variable_config: Dict,
        example_variable_dict: Dict):
    mock_four_d_context.datasets_ctx.get_ml_dataset.return_value = mock_ml_dataset
    mock_variable_id = "mock_dataset.mock_variable"
    with patch('xcube_4d_viewer.controllers._get_variable_value_range') as mock_get_variable_value_range, \
        patch('xcube_4d_viewer.controllers.get_variables') as mock_get_variables, \
            patch('xcube_4d_viewer.controllers._compute_tile_grid') as mock_compute_tile_grid:
        mock_get_variable_value_range.return_value = (0, 1)
        mock_get_variables.return_value = {mock_variable_id: example_variable_dict}
        mock_compute_tile_grid.return_value = example_variable_config['tile-grid']
        config = get_config_for_variable(mock_four_d_context, mock_variable_id)
    assert config == example_variable_config
