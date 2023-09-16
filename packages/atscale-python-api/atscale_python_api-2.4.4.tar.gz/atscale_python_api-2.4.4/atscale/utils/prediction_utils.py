import inspect
from math import e
from typing import List, Dict

from atscale.errors import atscale_errors
from atscale.base import enums
from atscale.data_model.data_model import DataModel
from atscale.parsers import project_parser
from atscale.db.sql_connection import SQLConnection
from atscale.utils import (
    query_utils,
    dmv_utils,
    model_utils,
    db_utils,
    validation_utils,
    feature_utils,
)
from atscale.base.enums import Aggs


def write_snowpark_udf_to_qds(
    data_model: DataModel,
    udf_name: str,
    new_feature_name: str,
    feature_inputs: List[str],
    publish: bool = True,
):
    """Writes a single column output of a udf into the given data_model as a feature. For example, if a
     udf created in snowpark 'udf' outputs predictions based on a given set of features '[f]', then calling
     write_udf_as_qds(data_model=atmodel, udf_name=udf, new_feature_name='predictions' feature_inputs=f)
     will create a new feature called 'predictions' which can be included in any query that excludes categorical features
     that are not accounted for in '[f]' (no feature not in same dimension at same level or lower in [f]). Currently only
     supports snowflake udfs.

    Args:
        data_model (DataModel): The AtScale data model to create the new feature in
        udf_name (str): The name of an existing udf which outputs a single column for every row of input.
            The full name space should be passed (ex. '"DB"."SCHEMA".udf_name').
        new_feature_name (str): The query name of the newly created feature from the output of the udf.
        feature_inputs (List[str]): The query names of features in data_model that are the inputs for the udf, in the order
            they are passed to the udf.
        publish (bool, optional): Whether to publish the project after updating, defaults to true.

    Raises:
        atscale_errors.UserError: When new_feature_name already exists as a feature in the given data_model, or any
        feature in feature_inputs does not exist in the given data_model.
    """
    model_utils._perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(write_snowpark_udf_to_qds),
    )

    feat_dict: dict = data_model.get_features(use_published=False)
    model_utils._check_conflicts(to_add=new_feature_name, preexisting=feat_dict)
    atscale_query: str = query_utils._generate_atscale_query(
        data_model=data_model, feature_list=feature_inputs
    )
    feature_query: str = query_utils.generate_db_query(
        data_model=data_model, atscale_query=atscale_query, use_aggs=False
    )
    categorical_inputs: List[str] = [
        feat for feat in feature_inputs if feat_dict[feat]["feature_type"] == "Categorical"
    ]
    categorical_string: str = ", ".join(f'"{cat}"' for cat in categorical_inputs)
    qds_query: str = (
        f"SELECT {_snowpark_udf_call(udf_name=udf_name, feature_inputs=feature_inputs)} "
        f'as "{new_feature_name}", {categorical_string} FROM ({feature_query})'
    )
    data_model.add_query_dataset(
        dataset_name=f"{new_feature_name}_QDS",
        query=qds_query,
        join_features=categorical_inputs,
        publish=False,
    )
    data_model.create_aggregate_feature(
        column_name=new_feature_name,
        fact_dataset_name=f"{new_feature_name}_QDS",
        name=new_feature_name,
        aggregation_type=enums.Aggs.SUM,  # could parameterize
        publish=publish,
    )


def join_udf(
    data_model: DataModel,
    target_columns: List[str],
    udf_call: str,
    join_columns: List[str] = None,
    join_features: List[str] = None,
    folder: str = None,
    qds_name: str = None,
    warehouse_id: str = None,
    allow_aggregates: bool = True,
    create_hinted_aggregate: bool = False,
    publish: bool = True,
):
    """Creates measures for each column in target_columns using the name that they are presented. For example,
    target_columns=['\"predicted_sales\" as \"sales_prediction\"', '\"confidence\"'] would make two measures named
    'sales_prediction' and 'confidence' respectively. The join_columns will be joined to join_features so that the
    target columns can be queried in tandem with the join_features and aggregate properly. If the join_columns already
    match the names of the categorical features in the data model, join_features can be omitted to use the names of the
    join_columns. The measures will be created from a QDS (Query Dataset) which uses the following query:
    'SELECT <target_column1, target_column2, ... target_columnN, join_column1, join_column2, ...> FROM <udf_call>'
    Each target column will have a sum aggregate feature created with "_SUM" appended to the column name.

    Args:
        data_model (DataModel): The AtScale data model to create the new features in
        target_columns (List[str]): A list of target columns which will be made into features, proper quoting for the
            data warehouse used is required. Feature names will be based on the name of the column as queried. These
            strings represent raw SQL and thus a target column can be a calculated column or udf call as long as it is
            proper SQL syntax.
        udf_call (str): A valid SQL statement that will be placed directly after a FROM clause and a space with no
        parenthesis.
        join_features (list, optional): a list of feature query names in the data model to use for joining. If None it will not
            join the qds to anything. Defaults to None for no joins.
        join_columns (list, optional): The columns in the from statement to join to the join_features. List must be
            either None or the same length and order as join_features. Defaults to None to use identical names to the
            join_features. If multiple columns are needed for a single join they should be in a nested list.
            Data warehouse specific quoting is not required, join_columns should be passed as strings and if quotes are
            required for the data model's data warehouse, they will be inserted automatically.
        folder (str): Optionally specifies a folder to put the created features in. If the folder does not exist it will
            be created.
        qds_name (str): Optionally specifies the name of Query Dataset that is created. Defaults to None to be named
            AI_LINK_UDF_QDS_<N> where <N> is 1 or the minimum number that doesn't conflict with existing dataset names.
        feature_inputs (List[str]): The query names of features in data_model that are the inputs for the udf, in the order
            they are passed to the udf.
        warehouse_id (str, optional): Defaults to None. The id of the warehouse that datasets in the data model query from.
            This parameter is only required if no dataset has been created in the data model yet.
        allow_aggregates(bool, optional): Whether to allow aggregates to be built off of the QDS. Defaults to True.
        create_hinted_aggregate(bool, optional): Whether to generate an aggregate table for all measures and keys in this QDS to improve join performance. Defaults to False.
        publish (bool): Defaults to True. Whether the updated project should be published or only the draft should be
            updated.

    Raises:
        atscale_errors.UserError: When new_feature_name already exists as a feature in the given data_model, or any
        feature in feature_inputs does not exist in the given data_model.
    """
    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(join_udf),
    )
    if join_features is None:
        join_features = []

    if join_columns is None:
        join_columns = join_features.copy()  # join_columns might get mutated
    elif len(join_features) != len(join_columns):
        raise atscale_errors.UserError(
            f"join_features and join_columns must be equal lengths. join_features is"
            f" length {len(join_features)} while join_columns is length {len(join_columns)}"
        )
    project_dict = data_model.project._get_dict()
    warehouse_id = validation_utils._validate_warehouse_id_parameter(
        atconn=data_model.project.atconn,
        project_dict=project_dict,
        warehouse_id=warehouse_id,
    )

    if qds_name is None:
        prefix = "AI_LINK_UDF_QDS_"
        all_dsets = project_parser.get_datasets(project_dict=project_dict)
        count = 1
        number_taken = {}
        for dset in all_dsets:
            if dset["name"][: len(prefix)] == prefix:
                try:
                    number_taken[int(dset["name"][len(prefix) :])] = True
                except:
                    pass
        while count in number_taken:
            count += 1
        qds_name = f"{prefix}{count}"
    db_platform: enums.PlatformType = data_model.project.atconn._get_warehouse_platform(
        warehouse_id=warehouse_id
    )
    db_conn: SQLConnection = db_utils.enum_to_dbconn(platform_type=db_platform)
    q: str = db_conn._column_quote()  # ex. Snowflake.column_quote(), its a static method

    join_column_strings = [f"{q}{j}{q}" for j in join_columns]
    qds_query = f'SELECT {", ".join(target_columns + join_column_strings)} FROM {udf_call}'

    columns = data_model.project.atconn.get_query_columns(
        warehouse_id=warehouse_id, query=qds_query
    )
    feat_dict: dict = data_model.get_features(use_published=False)
    columns_to_checks = [x[0] + "_SUM" for x in columns[: len(target_columns)]]
    model_utils._check_conflicts(to_add=columns_to_checks, preexisting=feat_dict)

    data_model.add_query_dataset(
        warehouse_id=warehouse_id,
        dataset_name=qds_name,
        query=qds_query,
        join_features=join_features,
        join_columns=join_columns,
        allow_aggregates=allow_aggregates,
        create_hinted_aggregate=create_hinted_aggregate,
        publish=False,
    )

    project_dict = data_model.project._get_dict()
    dset_id = project_parser.get_dataset(project_dict=project_dict, dataset_name=qds_name)["id"]
    for i in range(len(target_columns)):
        column_name = columns[i][0]
        feature_name = f"{column_name}_SUM"
        feature_utils._create_aggregate_feature_local(
            project_dict=project_dict,
            cube_id=data_model.cube_id,
            dataset_id=dset_id,
            column_name=column_name,
            name=feature_name,
            aggregation_type=Aggs.SUM,
            caption=feature_name,
            folder=folder,
        )
    data_model.project._update_project(project_json=project_dict, publish=publish)


def _write_regression_model_checks(
    model_type: enums.ScikitLearnModelType,
    data_model: DataModel,
    regression_model,
    new_feature_name: str,
):
    """A helper function for writing regression models to AtScale.

    Args:
        model_type (enums.ScikitLearnModelType): the type of scikit-learn model being written to AtScale.
        data_model (DataModel): The AtScale DataModel to add the regression into.
        regression_model (LinearRegression): The scikit-learn LinearRegression model to build into a feature.
        new_feature_name (str): The name of the created feature.

    Raises:
        atscale_errors.UserError: When the model passed is not a valid scikit-learn model.
        atscale_errors.UserError: When a feature already exists with new_feature_name.
        atscale_errors.ImportError: When scikit-learn is not installed.
    """
    try:
        if model_type == enums.ScikitLearnModelType.LINEARREGRESSION:
            from sklearn.linear_model import LinearRegression
        elif model_type == enums.ScikitLearnModelType.LOGISTICREGRESSION:
            from sklearn.linear_model import LogisticRegression
    except ImportError:
        raise ImportError(
            "scikit-learn needs to be installed to use this functionality, the function takes an "
            f"sklearn.linear_model.{model_type} object. Try running pip install scikit-learn"
        )

    model_failure = False

    if model_type == enums.ScikitLearnModelType.LINEARREGRESSION:
        if not isinstance(regression_model, LinearRegression):
            model_failure = True
    elif model_type == enums.ScikitLearnModelType.LOGISTICREGRESSION:
        if not isinstance(regression_model, LogisticRegression):
            model_failure = True

    if model_failure:
        raise atscale_errors.UserError(
            f"The model object of type: {type(regression_model)} is not compatible with this method "
            f"which takes an object of type sklearn.linear_model.{model_type}"
        )

    model_utils._check_conflicts(to_add=new_feature_name, data_model=data_model)


def _write_regression_model(
    model_type: enums.ScikitLearnModelType,
    data_model: DataModel,
    regression_model,
    new_feature_name: str,
    feature_inputs: List[str],
    granularity_levels: List[str],
):
    """A helper function for writing regression models to AtScale.

    Args:
        model_type (enums.ScikitLearnModelType): the type of scikit-learn model being written to AtScale.
        data_model (DataModel): The AtScale DataModel to add the regression into.
        regression_model (sklearn.linear_model): The scikit-learn linear model to build into a feature.
        new_feature_name (str): The name of the created feature.
        feature_inputs (List[str], optional): List of names of inputs features in the input order.
            Defaults to None to use the column names used when training the model.
        granularity_levels (List[str], optional): List of lowest categorical levels that predictions with this
            model can be run on. Defaults to False to use the lowest level from each hierarchy.
    """
    if granularity_levels is None:
        feature_dict = data_model.get_features(use_published=False)
        secondary_attributes = set()
        for feat, info in feature_dict.items():
            if info["feature_type"] == enums.FeatureType.CATEGORICAL.name_val:
                secondary_attribute = (
                    feat == info["hierarchy"][0]
                    and info.get("base_name", feat) != info.get("base_hierarchy", [""])[0]
                )
                if secondary_attribute:
                    secondary_attributes.add(feat)
        leaf_levels: List[str] = []
        hierarchy_to_levels: Dict["str", List[dict]] = dmv_utils.get_dmv_data(
            model=data_model,
            id_field=enums.Level.hierarchy,
            fields=[enums.Level.name, enums.Level.level_number],
        )
        for levels in hierarchy_to_levels.values():
            if type(levels["name"]) == list:
                leaf_levels.append(levels["name"][-1])
            elif levels["name"] not in secondary_attributes:
                leaf_levels.append(levels["name"])
        granularity_levels = leaf_levels

    if feature_inputs is None:
        feature_inputs = list(regression_model.feature_names_in_)

    atscale_query: str = query_utils._generate_atscale_query(
        data_model=data_model, feature_list=feature_inputs + granularity_levels
    )
    feature_query: str = query_utils.generate_db_query(
        data_model=data_model, atscale_query=atscale_query, use_aggs=False
    )
    categorical_string: str = ", ".join(f'"{cat}"' for cat in granularity_levels)
    numeric = " + ".join(
        [
            f'{theta1}*"{x}"'
            for theta1, x in zip(regression_model.coef_[0], regression_model.feature_names_in_)
        ]
    )
    numeric += f" + {regression_model.intercept_[0]}"
    if model_type == enums.ScikitLearnModelType.LINEARREGRESSION:
        qds_query: str = f'SELECT ({numeric}) as "{new_feature_name}"{", " if categorical_string else ""}{categorical_string} FROM ({feature_query})'
    elif model_type == enums.ScikitLearnModelType.LOGISTICREGRESSION:
        qds_query: str = f'SELECT ROUND(1 - 1 / (1 + POWER({e}, {numeric})), 0) as "{new_feature_name}" , {categorical_string} FROM ({feature_query})'
    data_model.add_query_dataset(
        dataset_name=f"{new_feature_name}_QDS",
        query=qds_query,
        join_features=granularity_levels,
    )
    data_model.create_aggregate_feature(
        column_name=new_feature_name,
        fact_dataset_name=f"{new_feature_name}_QDS",
        name=new_feature_name,
        aggregation_type=enums.Aggs.SUM,  # could parameterize
    )


def _snowpark_udf_call(
    udf_name: str,
    feature_inputs: List[str],
):
    inputs = ", ".join(f'"{f}"' for f in feature_inputs)
    return f"{udf_name}(array_construct({inputs}))"


def write_linear_regression_model(
    data_model: DataModel,
    regression_model,
    new_feature_name: str,
    granularity_levels: List[str] = None,
    feature_inputs: List[str] = None,
):
    """Writes a scikit-learn LinearRegression model, which takes AtScale features exclusively as input, to the given
    DataModel as a sum aggregated feature with the given name. The feature will return the output of the coefficients
    and intercept in the model applied to feature_inputs as defined in atscale. Omitting feature_inputs will use the
    names of the columns passed at training time and error if any names are not in the data model.

    Args:
        data_model (DataModel): The AtScale DataModel to add the regression into.
        regression_model (LinearRegression): The scikit-learn LinearRegression model to build into a feature.
        new_feature_name (str): The query name of the created feature.
        granularity_levels (List[str], optional): List of the query names for the lowest categorical levels that predictions with this
            model can be run on. Defaults to False to use the lowest level from each hierarchy.
        feature_inputs (List[str], optional): List of query names of inputs features in the input order.
            Defaults to None to use the column names used when training the model.

    Raises:
        atscale_errors.UserError: When the model passed is not a valid scikit-learn model.
        atscale_errors.UserError: When a feature already exists with new_feature_name.
        atscale_errors.ImportError: When scikit-learn is not installed.
    """
    model_utils._perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(write_linear_regression_model),
    )

    _write_regression_model_checks(
        enums.ScikitLearnModelType.LINEARREGRESSION,
        data_model,
        regression_model,
        new_feature_name,
    )

    _write_regression_model(
        enums.ScikitLearnModelType.LINEARREGRESSION,
        data_model,
        regression_model,
        new_feature_name,
        feature_inputs,
        granularity_levels,
    )


def write_logistic_regression_model(
    data_model: DataModel,
    regression_model,
    new_feature_name: str,
    granularity_levels: List[str] = None,
    feature_inputs: List[str] = None,
):
    """Writes a scikit-learn binary LogisticRegression model, which takes AtScale features exclusively as input, to the given
    DataModel as a sum aggregated feature with the given name. The feature will return the output of the coefficients
    and intercept in the model applied to feature_inputs as defined in atscale. Omitting feature_inputs will use the
    names of the columns passed at training time and error if any names are not in the data model.

    Args:
        data_model (DataModel): The AtScale DataModel to add the regression into.
        regression_model (LogisticRegression): The scikit-learn LogisticRegression model to build into a feature.
        new_feature_name (str): The query name of the created feature.
        granularity_levels (List[str], optional): List of the query names for the lowest categorical levels that predictions with this
            model can be run on. Defaults to False to use the lowest level from each hierarchy.
        feature_inputs (List[str], optional): List of query names of inputs features in the input order.
            Defaults to None to use the column names used when training the model.

    Raises:
        atscale_errors.UserError: When the model passed is not a valid scikit-learn model.
        atscale_errors.UserError: When a feature already exists with new_feature_name.
        atscale_errors.ImportError: When scikit-learn is not installed.
    """
    model_utils._perspective_check(data_model)

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(write_logistic_regression_model),
    )

    _write_regression_model_checks(
        enums.ScikitLearnModelType.LOGISTICREGRESSION,
        data_model,
        regression_model,
        new_feature_name,
    )

    # NOTE: Function only supports binary classification; AI-Link has not implemented multiclass support yet. We only support
    # binary classification until customer feedback indicates multiclass would be of use, as it is non-trivial to expand the logic.
    if len(regression_model.classes_) > 2:
        raise atscale_errors.UserError(
            f"write_logistic_regression_model only supports binary classification; model: "
            f"{regression_model} has more than two classes"
        )

    _write_regression_model(
        enums.ScikitLearnModelType.LOGISTICREGRESSION,
        data_model,
        regression_model,
        new_feature_name,
        feature_inputs,
        granularity_levels,
    )
