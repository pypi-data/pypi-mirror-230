import copy
import inspect
from typing import List

from atscale.base.enums import Hierarchy, Level, TimeSteps, FeatureType
from atscale.errors import atscale_errors
from atscale.utils import validation_utils
from atscale.utils.dmv_utils import get_dmv_data
from atscale.parsers import dictionary_parser as dparse
from atscale.data_model import data_model_helpers as dmh
from atscale.utils.feature_utils import (
    _check_time_hierarchy,
    _create_calculated_feature_local,
)
from atscale.utils.model_utils import (
    _check_features,
    _check_conflicts,
    _perspective_check,
)


def create_one_hot_encoded_features(
    data_model,
    categorical_feature: str,
    hierarchy_name: str = None,
    description: str = None,
    folder: str = None,
    format_string: str = None,
    publish: bool = True,
) -> List[str]:
    """Creates a one hot encoded feature for each value in the given categorical feature

    Args:
        data_model (DataModel): The data model to add the features to.
        categorical_feature (str): The query name of the categorical feature to pull the values from.
        hierarchy_name (str, optional): The query name of the hierarchy to use for the feature. Only necessary if the feature is duplicated in multiple hierarchies.
        description (str, optional): A description to add to the new features. Defaults to None.
        folder (str, optional): The folder to put the new features in. Defaults to None.
        format_string (str, optional): A format sting for the new features. Defaults to None.
        publish (bool, optional): Whether to publish the project after creating the features. Defaults to True.

    Returns:
        List[str]: The query names of the newly created features
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_one_hot_encoded_features),
    )

    filter_by = {Level.name: [categorical_feature]}
    if hierarchy_name:
        filter_by[Level.hierarchy] = [hierarchy_name]
    level_heritage = get_dmv_data(
        model=data_model, fields=[Level.dimension, Level.hierarchy], filter_by=filter_by
    )

    if len(level_heritage) == 0:
        raise atscale_errors.UserError(f"Level: {categorical_feature} does not exist in the model")
    dimension = level_heritage[categorical_feature][Level.dimension.name]
    hierarchy = level_heritage[categorical_feature][Level.hierarchy.name]
    df_values = data_model.get_data([categorical_feature], gen_aggs=False)
    project_json = data_model.project._get_dict()
    original_proj_dict = copy.deepcopy(
        project_json
    )  # need to check that the new names were free BEFORE adding them
    created_names = []
    for value in df_values[categorical_feature].values:
        expression = f'IIF(ANCESTOR([{dimension}].[{hierarchy}].CurrentMember, [{dimension}].[{hierarchy}].[{categorical_feature}]).MEMBER_NAME="{value}",1,0)'
        name = f"{categorical_feature}_{value}"
        created_names.append(name)
        _create_calculated_feature_local(
            project_json,
            data_model.cube_id,
            name,
            expression,
            description=description,
            caption=None,
            folder=folder,
            format_string=format_string,
        )

    _check_conflicts(to_add=created_names, data_model=data_model, project_dict=original_proj_dict)
    data_model.project._update_project(project_json=project_json, publish=publish)
    return created_names


def create_percent_change(
    data_model,
    new_feature_name: str,
    numeric_feature_name: str,
    time_length: int,
    hierarchy_name: str,
    level_name: str,
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a time over time calculation

    Args:
        data_model (DataModel): The DataModel that the feature will be written into
        new_feature_name (str): The query name of the new feature
        numeric_feature_name (str): The query name of the numeric feature to use for the calculation
        time_length (int): The length of the lag
        hierarchy_name (str): The query name of the time hierarchy used in the calculation
        level_name (str): The query name of the level within the time hierarchy
        description (str, optional): The description for the feature. Defaults to None. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_percent_change),
    )

    numerics = data_model.get_features(use_published=False, feature_type=FeatureType.NUMERIC)
    _check_features(
        features=[numeric_feature_name],
        check_list=numerics,
        errmsg=f"Invalid parameter value '{numeric_feature_name}' is not a numeric feature in the data model",
    )

    if not (type(time_length) == int) or time_length <= 0:
        raise atscale_errors.UserError(
            f"Invalid parameter value '{time_length}', Length must be an integer greater than zero"
        )

    hier_dict, level_dict = _check_time_hierarchy(
        data_model=data_model, hierarchy_name=hierarchy_name, level_name=level_name
    )

    time_dimension = hier_dict[hierarchy_name][Hierarchy.dimension.name]

    expression = (
        f"CASE WHEN IsEmpty((ParallelPeriod([{time_dimension}].[{hierarchy_name}].[{level_name}], {time_length}"
        f", [{time_dimension}].[{hierarchy_name}].CurrentMember), [Measures].[{numeric_feature_name}])) "
        f"THEN 0 ELSE ([Measures].[{numeric_feature_name}]"
        f"/(ParallelPeriod([{time_dimension}].[{hierarchy_name}].[{level_name}], {time_length}"
        f", [{time_dimension}].[{hierarchy_name}].CurrentMember), [Measures].[{numeric_feature_name}]) - 1) END"
    )
    data_model.create_calculated_feature(
        new_feature_name,
        expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
        publish=publish,
    )


def create_period_to_date(
    data_model,
    new_feature_name: str,
    numeric_feature_name: str,
    hierarchy_name: str,
    level_name: str,
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a period-to-date calculation

    Args:
        data_model (DataModel): The DataModel that the feature will be written into
        new_feature_name (str): The query name of the new feature
        numeric_feature_name (str): The query name of the numeric feature to use for the calculation
        hierarchy_name (str): The query name of the time hierarchy used in the calculation
        level_name (str): The query name of the level within the time hierarchy
        description (str, optional): The description for the feature. Defaults to None. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_period_to_date),
    )

    project_json = data_model.project._get_dict()
    existing_features = dmh._get_unpublished_features(project_dict=project_json)
    existing_measures = dparse.filter_dict(
        to_filter=existing_features,
        val_filters=[lambda i: i["feature_type"] == FeatureType.NUMERIC.name_val],
    )

    _check_features(
        features=[numeric_feature_name],
        check_list=list(existing_measures.keys()),
        errmsg=f"Invalid parameter value '{numeric_feature_name}' is not a numeric feature in the data model",
    )

    _check_conflicts(to_add=new_feature_name, preexisting=existing_features)

    hier_dict, level_dict = _check_time_hierarchy(
        data_model=data_model, hierarchy_name=hierarchy_name, level_name=level_name
    )

    time_dimension = hier_dict[hierarchy_name][Hierarchy.dimension.name]

    expression = (
        f"CASE WHEN IsEmpty([Measures].[{numeric_feature_name}]) THEN NULL ELSE "
        f"Sum(PeriodsToDate([{time_dimension}].[{hierarchy_name}].[{level_name}], "
        f"[{time_dimension}].[{hierarchy_name}].CurrentMember), [Measures].[{numeric_feature_name}]) END"
    )

    cube_id = data_model.cube_id
    _create_calculated_feature_local(
        project_json,
        cube_id,
        new_feature_name,
        expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
    )
    data_model.project._update_project(project_json=project_json, publish=publish)


def create_pct_error_calculation(
    data_model,
    new_feature_name: str,
    predicted_feature_name: str,
    actual_feature_name: str,
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a calculation for the percent error of a predictive feature compared to the actual feature

    Args:
        data_model (DataModel): The DataModel that the feature will be written into
        new_feature_name (str): The query name of the new feature
        predicted_feature_name (str): The query name of the feature containing predictions
        actual_feature_name (str): The query name of the feature to compare the predictions to
        description (str, optional): The description for the feature. Defaults to None. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_pct_error_calculation),
    )

    numerics = data_model.get_features(use_published=False, feature_type=FeatureType.NUMERIC)
    _check_features(
        [predicted_feature_name],
        numerics,
        f"Make sure '{predicted_feature_name}' is a numeric feature",
    )
    _check_features(
        [actual_feature_name],
        numerics,
        f"Make sure '{actual_feature_name}' is a numeric feature",
    )

    expression = (
        f"100*([Measures].[{predicted_feature_name}] - [Measures].[{actual_feature_name}]) / "
        f"[Measures].[{actual_feature_name}]"
    )
    data_model.create_calculated_feature(
        new_feature_name,
        expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
        publish=publish,
    )


def create_scaled_feature_minmax(
    data_model,
    new_feature_name: str,
    numeric_feature_name: str,
    min: float,
    max: float,
    feature_min: float = 0,
    feature_max: float = 1,
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a new feature that is minmax scaled

    Args:
        data_model (DataModel): The DataModel that the feature will be written into
        new_feature_name (str): The query name of the new feature
        numeric_feature_name (str): The query name of the feature to scale
        min (float): The min from the base feature
        max (float): The max from the base feature
        feature_min (float, optional): The min for the scaled feature. Defaults to 0.
        feature_max (float, optional): The max for the scaled feature. Defaults to 1.
        description (str, optional): The description for the feature. Defaults to None. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_scaled_feature_minmax),
    )

    expression = (
        f"(([Measures].[{numeric_feature_name}] - {min})/({max}-{min}))"
        f"*({feature_max}-{feature_min})+{feature_min}"
    )

    data_model.create_calculated_feature(
        new_feature_name,
        expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
        publish=publish,
    )


def create_scaled_feature_z_score(
    data_model,
    new_feature_name: str,
    numeric_feature_name: str,
    mean: float = 0,
    standard_deviation: float = 1,
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a new feature that is standard scaled

    Args:
        data_model (DataModel): The DataModel that the feature will be written into
        new_feature_name (str): The query name of the new feature
        numeric_feature_name (str): The query name of the feature to scale
        mean (float, optional): The mean from the base feature. Defaults to 0.
        standard_deviation (float, optional): The standard deviation from the base feature. Defaults to 1.
        description (str, optional): The description for the feature. Defaults to None. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_scaled_feature_z_score),
    )

    expression = f"([Measures].[{numeric_feature_name}] - {mean}) / {standard_deviation}"

    data_model.create_calculated_feature(
        new_feature_name,
        expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
        publish=publish,
    )


def create_scaled_feature_maxabs(
    data_model,
    new_feature_name: str,
    numeric_feature_name: str,
    maxabs: float,
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a new feature that is maxabs scaled

    Args:
        data_model (DataModel): The DataModel that the feature will be written into
        new_feature_name (str): The query name of the new feature
        numeric_feature_name (str): The query name of the feature to scale
        maxabs (float): The max absolute value of any data point from the base feature
        description (str, optional): The description for the feature. Defaults to None. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_scaled_feature_maxabs),
    )

    maxabs = abs(maxabs)
    expression = f"[Measures].[{numeric_feature_name}] / {maxabs}"

    data_model.create_calculated_feature(
        new_feature_name,
        expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
        publish=publish,
    )


def create_scaled_feature_robust(
    data_model,
    new_feature_name: str,
    numeric_feature_name: str,
    median: float = 0,
    interquartile_range: float = 1,
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a new feature that is robust scaled; mirrors default behavior of scikit-learn.preprocessing.RobustScaler

    Args:
        data_model (DataModel): The DataModel that the feature will be written into
        new_feature_name (str): The query name of the new feature
        numeric_feature_name (str): The query name of the feature to scale
        median (float, optional): _description_. Defaults to 0.
        interquartile_range (float, optional): _description_. Defaults to 1.
        description (str, optional): The description for the feature. Defaults to None. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_scaled_feature_robust),
    )

    expression = f"([Measures].[{numeric_feature_name}] - {median}) / {interquartile_range}"

    data_model.create_calculated_feature(
        new_feature_name,
        expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
        publish=publish,
    )


def create_scaled_feature_log_transformed(
    data_model,
    new_feature_name: str,
    numeric_feature_name: str,
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a new feature that is log transformed

    Args:
        data_model (DataModel): The DataModel that the feature will be written into
        new_feature_name (str): The query name of the new feature
        numeric_feature_name (str): The query name of the feature to scale
        description (str, optional): The description for the feature. Defaults to None. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_scaled_feature_log_transformed),
    )

    expression = f"log([Measures].[{numeric_feature_name}])"

    data_model.create_calculated_feature(
        new_feature_name,
        expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
        publish=publish,
    )


def create_scaled_feature_unit_vector_norm(
    data_model,
    new_feature_name: str,
    numeric_feature_name: str,
    magnitude: float,
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a new feature that is unit vector normalized

    Args:
        data_model (DataModel): The DataModel that the feature will be written into
        new_feature_name (str): The query name of the new feature
        numeric_feature_name (str): The query name of the feature to scale
        magnitude (float): The magnitude of the base feature, i.e. the square root of the sum of the squares of numeric_feature's data points
        description (str, optional): The description for the feature. Defaults to None. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_scaled_feature_unit_vector_norm),
    )

    expression = f"[Measures].[{numeric_feature_name}]/{magnitude}"

    data_model.create_calculated_feature(
        new_feature_name,
        expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
        publish=publish,
    )


def create_scaled_feature_power_transformed(
    data_model,
    new_feature_name: str,
    numeric_feature_name: str,
    power: float,
    method: str = "yeo-johnson",
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a new feature that is power transformed. Parameter 'method' must be either 'box-cox' or 'yeo-johnson'

    Args:
        data_model (DataModel): The DataModel that the feature will be written into
        new_feature_name (str): The query name of the new feature
        numeric_feature_name (str): The query name of the feature to scale
        power (float): The exponent used in the scaling
        method (str, optional): Which power transformation method to use. Defaults to 'yeo-johnson'.
        description (str, optional): The description for the feature. Defaults to None. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.

    Raises:
        atscale_errors.UserError: User must pass either of two valid power transformation methods
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_scaled_feature_power_transformed),
    )

    if method.lower() == "yeo-johnson":
        if power == 0:
            expression = (
                f"IIF([Measures].[{numeric_feature_name}]<0,"
                f"(-1*((((-1*[Measures].[{numeric_feature_name}])+1)^(2-{power}))-1))"
                f"/(2-{power}),log([Measures].[{numeric_feature_name}]+1))"
            )
        elif power == 2:
            expression = (
                f"IIF([Measures].[{numeric_feature_name}]<0,"
                f"(-1*log((-1*[Measures].[{numeric_feature_name}])+1)),"
                f"((([Measures].[{numeric_feature_name}]+1)^{power})-1)/{power})"
            )
        else:
            expression = (
                f"IIF([Measures].[{numeric_feature_name}]<0,"
                f"(-1*((((-1*[Measures].[{numeric_feature_name}])+1)^(2-{power}))-1))/(2-{power}),"
                f"((([Measures].[{numeric_feature_name}]+1)^{power})-1)/{power})"
            )
    elif method.lower() == "box-cox":
        if power == 0:
            expression = f"log([Measures].[{numeric_feature_name}])"
        else:
            expression = f"(([Measures].[{numeric_feature_name}]^{power})-1)/{power}"
    else:
        raise atscale_errors.UserError("Invalid type: Valid values are yeo-johnson and box-cox")

    data_model.create_calculated_feature(
        new_feature_name,
        expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
        publish=publish,
    )


def create_net_error_calculation(
    data_model,
    new_feature_name: str,
    predicted_feature_name: str,
    actual_feature_name: str,
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a calculation for the net error of a predictive feature compared to the actual feature

    Args:
        data_model (DataModel): The Data Model that the feature will be created in
        new_feature_name (str): The query name of the new feature
        predicted_feature_name (str): The query name of the feature containing predictions
        actual_feature_name (str): The query name of the feature to compare the predictions to
        description (str, optional): The description for the feature. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the created feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_net_error_calculation),
    )

    project_dict = data_model.project._get_dict()
    measure_list = dmh._get_unpublished_features(
        project_dict=project_dict,
        data_model_name=data_model.name,
        feature_type=FeatureType.NUMERIC,
    )
    _check_features(
        [predicted_feature_name],
        measure_list,
        f"Invalid parameter value '{predicted_feature_name}' "
        f"is not a numeric feature in the data model",
    )
    _check_features(
        [actual_feature_name],
        measure_list,
        f"Invalid parameter value '{actual_feature_name}' "
        f"is not a numeric feature in the data model",
    )
    level_list = dmh._get_unpublished_features(
        project_dict=project_dict,
        data_model_name=data_model.name,
        feature_type=FeatureType.CATEGORICAL,
    )
    preexisting = measure_list
    preexisting.update(level_list)
    _check_conflicts(to_add=new_feature_name, preexisting=preexisting)

    expression = f"[Measures].[{predicted_feature_name}] - [Measures].[{actual_feature_name}]"
    _create_calculated_feature_local(
        project_dict=project_dict,
        cube_id=data_model.cube_id,
        name=new_feature_name,
        expression=expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
    )
    data_model.project._update_project(project_json=project_dict, publish=publish)


def create_binned_feature(
    data_model,
    new_feature_name: str,
    numeric_feature_name: str,
    bin_edges: List[float],
    description: str = None,
    caption: str = None,
    folder: str = None,
    format_string: str = None,
    visible: bool = True,
    publish: bool = True,
):
    """Creates a new feature that is a binned version of an existing numeric feature.

    Args:
        data_model (DataModel): The DataModel that the feature will be written into
        new_feature_name (str): The query name of the new feature
        numeric_feature_name (str): The query name of the feature to bin
        bin_edges (List[float]): The edges to use to compute the bins, left inclusive. Contents of bin_edges are interpreted
                                 in ascending order
        description (str, optional): The description for the feature. Defaults to None.
        caption (str, optional): The caption for the feature. Defaults to None.
        folder (str, optional): The folder to put the feature in. Defaults to None.
        format_string (str, optional): The format string for the feature. Defaults to None.
        visible (bool, optional): Whether the created feature will be visible to BI tools. Defaults to True.
        publish (bool, optional): Whether or not the updated project should be published. Defaults to True.
    """
    # check if the provided data_model is a perspective
    _perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(create_binned_feature),
    )

    bin_edges = sorted(bin_edges)
    expression = f"CASE [Measures].[{numeric_feature_name}]"
    bin = 0
    for edge in bin_edges:
        expression += f" WHEN [Measures].[{numeric_feature_name}] < {edge} THEN {bin}"
        bin += 1
    expression += f" ELSE {bin} END"

    data_model.create_calculated_feature(
        new_feature_name,
        expression,
        description=description,
        caption=caption,
        folder=folder,
        format_string=format_string,
        visible=visible,
        publish=publish,
    )


def generate_time_series_features(
    data_model,
    dataframe,
    numeric_features: List[str],
    time_hierarchy: str,
    level: str,
    group_features: List[str] = None,
    intervals: List[int] = None,
    shift_amount: int = 0,
):
    """Generates time series features like rolling statistics and period to date for the given numeric features
     using the time hierarchy from the given data model

    Args:
        data_model (DataModel): The data model to use.
        dataframe (pandas.DataFrame): the pandas dataframe with the features.
        numeric_features (List[str]): The list of numeric feature query names to build time series features of.
        time_hierarchy (str): The query names of the time hierarchy to use to derive features.
        level (str): The query name of the level within the time hierarchy to derive the features at.
        group_features (List[str], optional): _description_. Defaults to None.
        intervals (List[int], optional): The intervals to create the features over.
            Will use default values based on the time step of the given level if None. Defaults to None.
        shift_amount (int, optional): The amount of rows to shift the new features. Defaults to 0.

    Returns:
        DataFrame: A DataFrame containing the original columns and the newly generated ones
    """
    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(generate_time_series_features),
    )

    hierarchy_dict, level_dict = _check_time_hierarchy(
        data_model=data_model, hierarchy_name=time_hierarchy, level_name=level
    )

    measure_list = data_model.get_features(use_published=True, feature_type=FeatureType.NUMERIC)
    categorical_list = data_model.get_features(
        use_published=True, feature_type=FeatureType.CATEGORICAL
    )

    level_list = level_dict
    if group_features:
        if type(group_features) != list:
            group_features = [group_features]
        _check_features(
            group_features,
            categorical_list,
            errmsg="Make sure all items in group_features are categorical features",
        )

    if type(numeric_features) != list:
        numeric_features = [numeric_features]
    _check_features(
        numeric_features,
        measure_list,
        errmsg="Make sure all items in numeric_features are numeric features",
    )

    time_numeric = level_dict[level][Level.type.name]
    # takes out the Time and 's' at the end and in lowercase
    time_name = str(time_numeric)[4:-1].lower()

    if intervals:
        if type(intervals) != list:
            intervals = [intervals]
    else:
        intervals = TimeSteps[time_numeric].get_steps()

    shift_name = f"_shift_{shift_amount}" if shift_amount != 0 else ""

    levels = [x for x in level_list if x in dataframe.columns]

    if group_features:
        dataframe = dataframe.sort_values(by=group_features + levels).reset_index(drop=True)
    else:
        dataframe = dataframe.sort_values(by=levels).reset_index(drop=True)

    for feature in numeric_features:
        for interval in intervals:
            interval = int(interval)
            name = feature + f"_{interval}_{time_name}_"
            if group_features:

                def grouper(x):
                    return x.groupby(group_features)

            else:

                def grouper(x):
                    return x

                # set this to an empty list so we can add it to hier_level later no matter what
                group_features = []
            if interval > 1:
                dataframe[f"{name}sum{shift_name}"] = (
                    grouper(dataframe)[feature]
                    .rolling(interval)
                    .sum()
                    .shift(shift_amount)
                    .reset_index(drop=True)
                )

                dataframe[f"{name}avg{shift_name}"] = (
                    grouper(dataframe)[feature]
                    .rolling(interval)
                    .mean()
                    .shift(shift_amount)
                    .reset_index(drop=True)
                )

                dataframe[f"{name}stddev{shift_name}"] = (
                    grouper(dataframe)[feature]
                    .rolling(interval)
                    .std()
                    .shift(shift_amount)
                    .reset_index(drop=True)
                )

                dataframe[f"{name}min{shift_name}"] = (
                    grouper(dataframe)[feature]
                    .rolling(interval)
                    .min()
                    .shift(shift_amount)
                    .reset_index(drop=True)
                )

                dataframe[f"{name}max{shift_name}"] = (
                    grouper(dataframe)[feature]
                    .rolling(interval)
                    .max()
                    .shift(shift_amount)
                    .reset_index(drop=True)
                )

            dataframe[f"{name}lag{shift_name}"] = (
                grouper(dataframe)[feature]
                .shift(interval)
                .shift(shift_amount)
                .reset_index(drop=True)
            )

        found = False
        for heir_level in reversed(levels):
            if found and heir_level in dataframe.columns:
                name = f"{feature}_{heir_level}_to_date"
                dataframe[name] = (
                    dataframe.groupby(group_features + [heir_level])[feature]
                    .cumsum()
                    .shift(shift_amount)
                    .reset_index(drop=True)
                )
            if heir_level == level:
                found = True

    return dataframe
