"""Defines parameters for route handlers in routes.py."""

PATH_PARAM_X = {
    "name": "x",
    "in": "path",
    "description": "The tile grid's x-coordinate",
    "schema": {
        "type": "integer",
    }
}

PATH_PARAM_Y = {
    "name": "y",
    "in": "path",
    "description": "The tile grid's y-coordinate",
    "schema": {
        "type": "integer",
    }
}

PATH_PARAM_Z = {
    "name": "z",
    "in": "path",
    "description": "The tile grid's z-coordinate",
    "schema": {
        "type": "integer",
    }
}

PATH_PARAM_VAR_ID = {
    "name": "variable_id",
    "in": "path",
    "description": "The variable id in form <dataset_id>.<variable_name>",
    "schema": {
        "type": "string",
    }
}

PATH_PARAM_TIME = {
    "name": "time_index",
    "in": "path",
    "description": "The time index",
    "schema": {
        "type": "integer",
    }
}

PATH_PARAM_RESOLUTION = {
    "name": "resolution_index",
    "in": "path",
    "description": "The resolution index",
    "schema": {
        "type": "integer",
    }
}

PATH_PARAM_EXT = {
    "name": "extension",
    "in": "path",
    "description": "Extension of response",
    "schema": {
        "type": "string",
    }
}
