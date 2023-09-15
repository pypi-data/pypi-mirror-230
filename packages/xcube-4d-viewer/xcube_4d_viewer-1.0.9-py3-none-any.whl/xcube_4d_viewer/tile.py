"""Encapsulates tile data specification (and simplifies function signatures)."""
from __future__ import annotations

from xcube_4d_viewer.helpers.general_helpers import \
    variable_id_to_dataset_and_variable


class Tile:
    def __init__(self: Tile, variable_id: str, resolution_index: int, time_index: int,
                 x: int, y: int, extension: str, z: int = None) -> Tile:
        self.variable_id = variable_id
        self.dataset_id, self.variable_name = variable_id_to_dataset_and_variable(variable_id=variable_id)
        self.resolution_index = resolution_index
        self.x = x
        self.y = y
        self.z = z
        self.extension = extension
        self.time_index = time_index
