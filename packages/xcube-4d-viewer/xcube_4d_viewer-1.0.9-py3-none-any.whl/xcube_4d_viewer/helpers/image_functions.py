"""Set of image helpers."""
from __future__ import annotations

from dataclasses import dataclass
import io
from typing import List, Optional

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from xcube_4d_viewer.helpers.serialising import volume_to_bytes


@dataclass
class ColorLA:
    """Single channel + alpha color container - unity helper."""

    value: float    # This is better as a float for vertical resolution accuracy
    alpha: int      # We don't need accuracy here


def convert_array_to_image_bytes(tile_data: NDArray, dataset_type: str) -> bytes:
    if dataset_type == "heatmap3d":
        return volume_to_bytes(_convert_to_unity_image_3d(tile_data))
    else:
        tile_data_with_alpha_channel = np.zeros((tile_data.shape[0], tile_data.shape[1], 2),
                                                dtype=np.uint8)
        tile_data_with_alpha_channel[..., 0] = tile_data * 255
        tile_data_with_alpha_channel[..., 1] = np.where(np.isnan(tile_data), 0, 255)
        return _encode_as_png_image_bytes(tile_data_with_alpha_channel, "LA")


def pad_image_array(data: NDArray, new_dimension_sizes: List[int], pad_value: Optional[int] = 0) -> NDArray:
    assert len(data.shape) == len(new_dimension_sizes), (
        f"Data array has {len(data.shape)} dimensions but {len(new_dimension_sizes)} desired dimensions were passed")

    new_sizes = [(0, max(new_dimension_sizes[i] - data.shape[i], 0)) for i in range(len(new_dimension_sizes))]
    return np.pad(data, new_sizes, 'constant', constant_values=pad_value)


def _encode_as_png_image_bytes(data_array, img_mode):
    img = Image.fromarray(data_array, img_mode)

    stream = io.BytesIO()
    img.save(stream, format='PNG')
    return bytes(stream.getvalue())


def _convert_to_unity_image_3d(array: NDArray) -> NDArray:
    """
    Convert a data set array [Z, Y, X] into a unity friendly array of colors.

    Parameters
    ----------
    array : NDArray
        Data set array

    Returns
    -------
    NDArray
        Array of colors
    """
    color_depth = 255   # static value representing range of ints for a given pixel/rgba value
    z_size = array.shape[0]
    y_size = array.shape[1]
    x_size = array.shape[2]

    # Note here we switch y and z axis. Again for unity conventions (their Y is our Z and vice versa)
    result = np.zeros((y_size, z_size, x_size), dtype=ColorLA)

    # This is very slow - may need to avoid the type change and serialize directly from np array.
    for z in range(z_size):
        for y in range(y_size):
            for x in range(x_size):

                y_index = y_size - y - 1    # Flip y orientation for unity convention

                value = array[z, y_index, x]

                alpha = 0 if np.isnan(value) else color_depth
                value = 0 if np.isnan(value) else color_depth * value
                color = ColorLA(value, alpha)

                result[y, z, x] = color
    return result
