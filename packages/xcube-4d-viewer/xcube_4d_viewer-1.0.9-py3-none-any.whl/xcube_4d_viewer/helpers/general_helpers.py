"""General helpers module. Put here mainly to avoid circular imports for now."""
from typing import Tuple


def variable_id_to_dataset_and_variable(variable_id: str) -> Tuple[str, str]:
    """
    Extract dataset id and variable name from variable id, which is of the form <dataset_id>.<variable_name>.

    We need the dataset id and var name to call other components of the xcube repo. The concept of a variable in xcube
    maps to the definition of a dataset within the middle tier and 4D client, which is why variable_id is used in all
    the endpoints of the xcube_4d_viewer API. It is a unique identifier of a separate portion of data.

    Parameters
    ----------
    variable_id : str
        Variable id of the form <dataset_id>.<variable_name>

    Returns
    -------
    Tuple[str, str]
        Tuple representing[dataset_id, variable_name]
    """
    variable_id_components = variable_id.split(".")
    if len(variable_id_components) < 2:
        raise ValueError(f"Variable id {variable_id} is invalid.")
    dataset_id = ".".join(variable_id_components[:-1]).replace('@', '~')
    variable_name = variable_id_components[-1]
    return dataset_id, variable_name
