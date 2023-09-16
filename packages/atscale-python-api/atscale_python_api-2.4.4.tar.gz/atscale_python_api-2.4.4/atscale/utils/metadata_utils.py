from typing import List, Dict

from atscale.utils.dmv_utils import get_dmv_data
from atscale.base.enums import Measure, Level, Hierarchy, Dimension, FeatureType


def _get_dimensions(data_model, filter_by: Dict[Dimension, List[str]] = None) -> dict:
    """Gets a dictionary of dictionaries with the dimension names and metadata.

    Args:
        data_model (DataModel): The DataModel object to search through
        filter_by (dict[Dimension fields, str], optional): A dict with keys of fields and values of a list of that field's value
                to exclusively include in the return. Defaults to None for no filtering.

    Returns:
        dict: A dictionary of dictionaries where the dimension names are the keys in the outer dictionary
              while the inner keys are the following: 'description', 'type'(value is Time
              or Standard).
    """
    dimension_dict = get_dmv_data(
        model=data_model,
        fields=[
            Dimension.description,
            Dimension.type,
        ],
        filter_by=filter_by,
    )
    dimensions = {}
    for name, info in dimension_dict.items():
        dimensions[name] = {
            "description": info[Dimension.description.name],
            "type": info[Dimension.type.name],
        }
    return dimensions


def _get_hierarchies(
    data_model,
    filter_by: Dict[Hierarchy, List[str]] = None,
) -> dict:
    """Gets a dictionary of dictionaries with the hierarchies names and metadata.
    Secondary attributes are treated as their own hierarchies.

    Args:
        data_model (DataModel): The DataModel object to search through
        filter_by (dict[Hierarchy fields, str], optional): A dict with keys of fields and values of a list of that field's value
                to exclusively include in the return. Defaults to None for no filtering.

    Returns:
        dict: A dictionary of dictionaries where the hierarchy names are the keys in the outer dictionary
              while the inner keys are the following: 'dimension', 'description', 'caption', 'folder', 'type'(value is Time
              or Standard), 'secondary_attribute'.
    """
    hierarchy_dict = get_dmv_data(
        model=data_model,
        fields=[
            Hierarchy.dimension,
            Hierarchy.description,
            Hierarchy.folder,
            Hierarchy.caption,
            Hierarchy.type,
            Hierarchy.secondary_attribute,
        ],
        filter_by=filter_by,
    )
    hierarchies = {}
    for name, info in hierarchy_dict.items():
        hierarchies[name] = {
            "dimension": info[Hierarchy.dimension.name],
            "description": info[Hierarchy.description.name],
            "caption": info[Hierarchy.caption.name],
            "folder": info[Hierarchy.folder.name],
            "type": info[Hierarchy.type.name],
            "secondary_attribute": info[Hierarchy.secondary_attribute.name],
        }
    return hierarchies


def _get_hierarchy_levels(
    data_model,
    hierarchy_name: str,
) -> List[str]:
    """Gets a list of the levels of a given hierarchy

    Args:
        data_model (DataModel): The DataModel object the given hierarchy exists within.
        hierarchy_name (str): The name of the hierarchy

    Returns:
        List[str]: A list containing the hierarchy's levels
    """

    levels_from_hierarchy = get_dmv_data(
        model=data_model,
        fields=[Level.name],
        id_field=Level.hierarchy,
        filter_by={Level.hierarchy: [hierarchy_name]},
    )

    hierarchy = levels_from_hierarchy.get(hierarchy_name)
    if hierarchy:
        levels = hierarchy.get(Level.name.name, [])
        if type(levels) is list:
            return levels
        else:
            return [levels]
    else:
        return []


def _get_feature_description(
    data_model,
    feature: str,
) -> str:
    """Returns the description of a given feature given the DataModel containing it.

    Args:
        data_model (DataModel): The DataModel object the given feature exists within.
        feature (str): The query name of the feature to retrieve the description of.

    Returns:
        str: The description of the given feature.
    """
    return data_model.get_features(feature_list=[feature])[feature]["description"]


def _get_feature_expression(
    data_model,
    feature: str,
) -> str:
    """Returns the expression of a given feature given the DataModel containing it.

    Args:
        data_model (DataModel): The DataModel object the given feature exists in.
        feature (str): The query name of the feature to return the expression of.

    Returns:
        str: The expression of the given feature.
    """
    return data_model.get_features(feature_list=[feature])[feature]["expression"]


def _get_all_numeric_feature_names(
    data_model,
    folder: str = None,
) -> List[str]:
    """Returns a list of all numeric features (ie Aggregate and Calculated Measures) in a given data model.

    Args:
        data_model (DataModel): The DataModel object to be queried.
        folder (str, optional): The name of a folder in the data model containing measures to exclusively list.
            Defaults to None to not filter by folder.

    Returns:
        List[str]: A list of the query names of numeric features in the data model and, if given, in the folder.
    """
    folders = [folder] if folder else None
    return list(
        data_model.get_features(folder_list=folders, feature_type=FeatureType.NUMERIC).keys()
    )


def _get_all_categorical_feature_names(
    data_model,
    folder: str = None,
) -> List[str]:
    """Returns a list of all categorical features (ie Hierarchy levels and secondary_attributes) in a given DataModel.

    Args:
        data_model (DataModel): The DataModel object to be queried.
        folder (str, optional): The name of a folder in the DataModel containing features to exclusively list.
            Defaults to None to not filter by folder.

    Returns:
        List[str]: A list of the query names of categorical features in the DataModel and, if given, in the folder.
    """
    folders = [folder] if folder else None
    return list(
        data_model.get_features(folder_list=folders, feature_type=FeatureType.CATEGORICAL).keys()
    )


def _get_folders(
    data_model,
) -> List[str]:
    """Returns a list of the available folders in a given DataModel.

    Args:
        data_model (DataModel): The DataModel object to be queried.

    Returns:
        List[str]: A list of the available folders
    """

    measure_dict = get_dmv_data(model=data_model, fields=[Measure.folder])

    hierarchy_dict = get_dmv_data(model=data_model, fields=[Hierarchy.folder])

    folders = sorted(
        set(
            [measure_dict[key]["folder"] for key in measure_dict.keys()]
            + [hierarchy_dict[key]["folder"] for key in hierarchy_dict.keys()]
        )
    )
    if "" in folders:
        folders.remove("")
    return folders
