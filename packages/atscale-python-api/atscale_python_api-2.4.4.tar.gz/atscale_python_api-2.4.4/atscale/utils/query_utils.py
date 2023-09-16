import datetime
import inspect
import json
import re
import logging
from typing import Dict, List, Tuple

from atscale.errors import atscale_errors
from atscale.base import config
from atscale.parsers import project_parser
from atscale.data_model import data_model_helpers
from atscale.utils import model_utils
from atscale.utils import validation_utils
from atscale.base.enums import RequestType, FeatureType
from atscale.base import endpoints

logger = logging.getLogger(__name__)


def _generate_atscale_query(
    data_model,
    feature_list: List[str],
    filter_equals: Dict[str, str] = None,
    filter_greater: Dict[str, str] = None,
    filter_less: Dict[str, str] = None,
    filter_greater_or_equal: Dict[str, str] = None,
    filter_less_or_equal: Dict[str, str] = None,
    filter_not_equal: Dict[str, str] = None,
    filter_in: Dict[str, List[str]] = None,
    filter_between: Dict[str, Tuple[str, str]] = None,
    filter_like: Dict[str, str] = None,
    filter_rlike: Dict[str, str] = None,
    filter_null: List[str] = None,
    filter_not_null: List[str] = None,
    order_by: List[Tuple[str, str]] = None,
    limit: int = None,
    comment: str = None,
    use_aggs: bool = True,
    gen_aggs: bool = True,
    raise_multikey_warning: bool = True,
) -> str:
    """Generates an AtScale query to get the given features.

    Args:
        data_model (DataModel): The AtScale DataModel that the generated query interacts with.
        feature_list (List[str]): The list query names for the features to query.
        filter_equals (Dict[str:str], optional): Filters results based on the feature equaling the value. Defaults
             to None
        filter_greater (Dict[str:str], optional): Filters results based on the feature being greater than the value.
             Defaults to None
        filter_less (Dict[str:str], optional): Filters results based on the feature being less than the value.
            Defaults to None
        filter_greater_or_equal (Dict[str:str], optional): Filters results based on the feature being greater or
            equaling the value. Defaults to None
        filter_less_or_equal (Dict[str:str], optional): Filters results based on the feature being less or equaling
            the value. Defaults to None
        filter_not_equal (Dict[str:str], optional): Filters results based on the feature not equaling the value.
            Defaults to None
        filter_in (Dict[str:List(str)], optional): Filters results based on the feature being contained in the values.
            Takes in a list of str as the dictionary values. Defaults to None
        filter_between (Dict[str:(str,str)], optional): Filters results based on the feature being between the values.
             Defaults to None
        filter_like (Dict[str:str], optional): Filters results based on the feature being like the clause. Defaults
            to None
        filter_rlike (Dict[str:str], optional): Filters results based on the feature being matched by the regular
            expression. Defaults to None
        filter_null (Dict[str:str], optional): Filters results to show null values of the specified features.
            Defaults to None
        filter_not_null (Dict[str:str], optional): Filters results to exclude null values of the specified
            features. Defaults to None
        order_by (List[Tuple[str, str]]): The sort order for the query. Accepts a list of tuples of the
                feature query name and ordering respectively: [('feature_name_1', 'DESC'), ('feature_2', 'ASC') ...].
                Defaults to None for AtScale Engine default sorting.
        limit (int, optional): Limit the number of results. Defaults to None for no limit.
        comment (str, optional): A comment string to build into the query. Defaults to None for no comment.

    Returns:
        str: An AtScale query string
    """
    inspection = inspect.getfullargspec(_generate_atscale_query)
    validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

    filter_equals = {} if filter_equals is None else filter_equals
    filter_greater = {} if filter_greater is None else filter_greater
    filter_less = {} if filter_less is None else filter_less
    filter_greater_or_equal = {} if filter_greater_or_equal is None else filter_greater_or_equal
    filter_less_or_equal = {} if filter_less_or_equal is None else filter_less_or_equal
    filter_not_equal = {} if filter_not_equal is None else filter_not_equal
    filter_in = {} if filter_in is None else filter_in
    filter_between = {} if filter_between is None else filter_between
    filter_like = {} if filter_like is None else filter_like
    filter_rlike = {} if filter_rlike is None else filter_rlike
    filter_null = [] if filter_null is None else filter_null
    filter_not_null = [] if filter_not_null is None else filter_not_null
    order_by = [] if order_by is None else order_by

    # separate ordering features into a list to verify existence in the model while also turning tuples into 'feat DESC'
    ordering_strings = []
    ordering_features = []

    error_items = []
    for maybe_tuple in order_by:
        if not (
            isinstance(maybe_tuple, tuple)
            and len(maybe_tuple) == 2
            and isinstance(maybe_tuple[0], str)
            and isinstance(maybe_tuple[1], str)
            and maybe_tuple[1].upper() in ["ASC", "DESC"]
        ):
            error_items.append(maybe_tuple)
        else:
            ordering_strings.append(f"`{maybe_tuple[0]}` {maybe_tuple[1].upper()}")
            ordering_features.append(maybe_tuple[0])

    if error_items:
        raise atscale_errors.UserError(
            f"All items in the order_by parameter must be a tuple of a "
            f'feature name then "ASC" or "DESC". The following do not '
            f"comply: {error_items}"
        )

    all_features = data_model.get_features()
    list_all = set(
        all_features
    )  # turns it into a set of the keys and has constant time lookup on average

    model_utils._check_features(feature_list, list_all)

    deduped_feature_list = []  # need to remove duplicates before sending to engine
    feature_set = set()
    repeats = []
    for f in feature_list:
        if f not in feature_set:
            deduped_feature_list.append(f)
            feature_set.add(f)
        else:
            repeats.append(f)
    if repeats:
        logger.info(
            f"The following feature names appear more than once in the feature_list parameter: {repeats}. "
            f"Any repeat occurrences have been omitted."
        )
    feature_list = deduped_feature_list

    # check to make sure no columns of a multi-key are excluded
    if raise_multikey_warning:
        project_dict = data_model.project._get_dict()

        # get the subset of all columns that are non-measures and then see if any of the features overlap
        # todo: find a better spot for _get_unpublished_features and avoid the extra _get_dict() call
        categoricals = data_model_helpers._get_unpublished_features(
            project_dict=project_dict,
            data_model_name=data_model.name,
            feature_type=FeatureType.CATEGORICAL,
        )
        features_to_validate = {
            f: categoricals[f].get("base_name", f) for f in feature_list if f in categoricals
        }

        if features_to_validate:
            features_needed = project_parser._get_feature_keys(
                project_dict=project_dict,
                cube_id=data_model.cube_id,
                join_features=list(features_to_validate.values()),
            )

            for feature_name, base_name in features_to_validate.items():
                key_columns = features_needed[base_name]["key_cols"]
                if len(key_columns) > 1:
                    logger.warning(
                        f"Feature: {feature_name} has a compound key, "
                        f"features representing all key columns {key_columns} should "
                        f"be included to avoid ambiguous results"
                    )

    # check elements of the filters
    list_params = [
        filter_equals,
        filter_greater,
        filter_less,
        filter_greater_or_equal,
        filter_less_or_equal,
        filter_not_equal,
        filter_in,
        filter_between,
        filter_like,
        filter_rlike,
        filter_null,
        filter_not_null,
    ]
    for param in list_params + [ordering_features]:
        model_utils._check_features(param, list_all)

    if ordering_strings:
        order_string = f' ORDER BY {", ".join(ordering_strings)}'
    else:
        categorical_columns = [
            f"`{name}`"
            for name, metadata in all_features.items()
            if metadata["feature_type"].upper() == FeatureType.CATEGORICAL.name
        ]
        order_string = f' ORDER BY {", ".join(categorical_columns)}'

    all_columns_string = " " + ", ".join(f"`{x}`" for x in feature_list)

    if any(list_params):
        filter_string = " WHERE ("
        for key, value in filter_equals.items():
            if filter_string != " WHERE (":
                filter_string += " and "
            if not isinstance(value, (int, float, bool)):
                filter_string += f"(`{key}` = '{value}')"
            else:
                filter_string += f"(`{key}` = {value})"
        for key, value in filter_greater.items():
            if filter_string != " WHERE (":
                filter_string += " and "
            if not isinstance(value, (int, float, bool)):
                filter_string += f"(`{key}` > '{value}')"
            else:
                filter_string += f"(`{key}` > {value})"
        for key, value in filter_less.items():
            if filter_string != " WHERE (":
                filter_string += " and "
            if not isinstance(value, (int, float, bool)):
                filter_string += f"(`{key}` < '{value}')"
            else:
                filter_string += f"(`{key}` < {value})"
        for key, value in filter_greater_or_equal.items():
            if filter_string != " WHERE (":
                filter_string += " and "
            if not isinstance(value, (int, float, bool)):
                filter_string += f"(`{key}` >= '{value}')"
            else:
                filter_string += f"(`{key}` >= {value})"
        for key, value in filter_less_or_equal.items():
            if filter_string != " WHERE (":
                filter_string += " and "
            if not isinstance(value, (int, float, bool)):
                filter_string += f"(`{key}` <= '{value}')"
            else:
                filter_string += f"(`{key}` <= {value})"
        for key, value in filter_not_equal.items():
            if filter_string != " WHERE (":
                filter_string += " and "
            if not isinstance(value, (int, float, bool)):
                filter_string += f"(`{key}` <> '{value}')"
            else:
                filter_string += f"(`{key}` <> {value})"
        for key, value in filter_like.items():
            if filter_string != " WHERE (":
                filter_string += " and "
            if not isinstance(value, (int, float, bool)):
                filter_string += f"(`{key}` LIKE '{value}')"
            else:
                filter_string += f"(`{key}` LIKE {value})"
        for key, value in filter_rlike.items():
            if filter_string != " WHERE (":
                filter_string += " and "
            filter_string += f"(`{key}` RLIKE '{value}')"
        for key, value in filter_in.items():
            str_values = [str(x) for x in value]
            if filter_string != " WHERE (":
                filter_string += " and "
            if not isinstance(value[0], (int, float, bool)):
                filter_string += f"(`{key}` IN ('"
                filter_string += "', '".join(str_values)
                filter_string += "'))"
            else:
                filter_string += f"(`{key}` IN ("
                filter_string += ", ".join(str_values)
                filter_string += "))"
        for key, value in filter_between.items():
            if filter_string != " WHERE (":
                filter_string += " and "
            if not isinstance(value[0], (int, float, bool)):
                filter_string += f"(`{key}` BETWEEN '{value[0]}' and '{value[1]}')"
            else:
                filter_string += f"(`{key}` BETWEEN {value[0]} and {value[1]})"
        for key in filter_null:
            if filter_string != " WHERE (":
                filter_string += " and "
            filter_string += f"(`{key}` IS NULL)"
        for key in filter_not_null:
            if filter_string != " WHERE (":
                filter_string += " and "
            filter_string += f"(`{key}` IS NOT NULL)"
        filter_string += ")"
    else:
        filter_string = ""

    if limit is None:
        limit_string = ""
    else:
        limit_string = f" LIMIT {limit}"

    if comment is None:
        comment_string = ""
    else:
        comment_string = f" /* {comment} */"

    version_comment = f" /* Python library version: {config.Config().version} */"

    if use_aggs:
        use_aggs_comment = ""
    else:
        use_aggs_comment = " /* use_aggs(false) */"
    if gen_aggs:
        gen_aggs_comment = ""
    else:
        gen_aggs_comment = " /* generate_aggs(false) */"

    query = (
        f"SELECT{use_aggs_comment}{gen_aggs_comment}{all_columns_string}"
        f" FROM `{data_model.project.project_name}`.`{data_model.name}`"
        f"{filter_string}{order_string}{limit_string}{comment_string}{version_comment}"
    )
    return query


def generate_db_query(
    data_model,
    atscale_query: str,
    use_aggs: bool = True,
    gen_aggs: bool = True,
    fake_results: bool = False,
    use_local_cache: bool = True,
    use_aggregate_cache: bool = True,
    timeout: int = 10,
) -> str:
    """Submits an AtScale query to the query planner and grabs the outbound query to the database which is returned.

    Args:
        data_model (DataModel): an atscale DataModel object
        atscale_query (str): an SQL query that references the atscale semantic layer (rather than the backing data warehouse)
        use_aggs (bool, optional): Whether to allow the query to use aggs. Defaults to True.
        gen_aggs (bool, optional): Whether to allow the query to generate aggs. Defaults to True.
        fake_results (bool, optional): Whether to use fake results. Defaults to False.
        use_local_cache (bool, optional): Whether to allow the query to use the local cache. Defaults to True.
        use_aggregate_cache (bool, optional): Whether to allow the query to use the aggregate cache. Defaults to True.
        timeout (int, optional): The number of minutes to wait for a response before timing out. Defaults to 10.

    Returns:
        str: the query that atscale would send to the backing data warehouse given the atscale_query sent to atscale
    """

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(generate_db_query),
    )

    # if the atscale_query already has a limit in the sql, we replace it with a limit 1
    limit_match = re.search(r"LIMIT [0-9]+", atscale_query)
    if limit_match:
        inbound_query = atscale_query.replace(limit_match.group(0), "LIMIT 1")
    else:
        inbound_query = f"{atscale_query} LIMIT 1"

    # we'll keep track of any comment so it can be added to the outbound query that is returned
    comment_match = re.findall(r"/\*.+?\*/", atscale_query)

    # we use a time stamp around the time we submit the query, to then query atscale to
    # try and get back the query it actually submitted to the backing data warehouse
    now = datetime.datetime.utcnow()  # current date and time
    now = now - datetime.timedelta(minutes=5)

    date_time = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    # Post the rest query through atscale. No return value, we have to dig through logs to see what it was later
    atconn = data_model.project.atconn
    published_project_name = data_model.project.published_project_name

    atconn._post_atscale_query(
        query=inbound_query,
        project_name=published_project_name,
        use_aggs=use_aggs,
        gen_aggs=gen_aggs,
        fake_results=fake_results,
        use_local_cache=use_local_cache,
        use_aggregate_cache=use_aggregate_cache,
        timeout=timeout,
    )

    url = endpoints._endpoint_query_view(
        atconn=atconn,
        suffix=f"&querySource=user&queryStarted=5m&queryDateTimeStart={date_time}",
    )

    response = atconn._submit_request(request_type=RequestType.GET, url=url)
    json_data = json.loads(response.content)["response"]
    db_query = ""

    for query_info in json_data["data"]:
        if db_query != "":
            break
        if query_info["query_text"] == inbound_query:
            for event in query_info["timeline_events"]:
                if event["type"] == "SubqueriesWall":
                    # check if it was truncated
                    if event["children"][0]["query_text_truncated"]:
                        url = endpoints._endpoint_design_private_org(
                            atconn=atconn,
                            suffix=f'/fullquerytext/queryId/{query_info["query_id"]}'
                            f'?subquery={event["children"][0]["query_id"]}',
                        )
                        response = atconn._submit_request(request_type=RequestType.GET, url=url)
                        outbound_query = response.text
                    else:
                        outbound_query = event["children"][0]["query_text"]
                    if (
                        limit_match
                    ):  # if there was a limit in the original query, replace our limit 1 with the original limit
                        db_query = outbound_query.replace("LIMIT 1", limit_match.group(0))
                        db_query = db_query.replace(
                            "TOP (1)", f"TOP ({limit_match.group(0).split()[1]})"
                        )
                    else:  # if there was no limit in the original query, then just remove ours
                        db_query = outbound_query.replace("LIMIT 1", "")
                        db_query = db_query.replace("TOP (1)", "")
                    if comment_match:  # add any comment to the outbound query
                        for comment in comment_match:
                            db_query += " "
                            db_query += comment

                    break
    return db_query
