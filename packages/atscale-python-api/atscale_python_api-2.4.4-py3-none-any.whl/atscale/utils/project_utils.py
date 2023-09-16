import json
import uuid
from typing import List, Tuple

from atscale.connection.connection import Connection
from atscale.base import endpoints
from atscale.parsers import project_parser
from atscale.base import templates
from atscale.base.enums import RequestType


def create_project(
    atconn: Connection,
    project_dict: dict,
):
    """Creates a new project using the project_dict provided

    Args:
        atconn (Connection): the connection to add the project with
        project_dict (Dict): the project metadata to build the project with

    Returns:
        Project: An instance of the Project object representing the new project
    """
    # creates a project with the given project dict
    u = endpoints._endpoint_design_org(atconn, "/project")
    response = atconn._submit_request(
        request_type=RequestType.POST, url=u, data=json.dumps(project_dict)
    )
    project_dict = json.loads(response.content)["response"]
    # now we'll use the values to construct a python Project class
    project_id = project_dict.get("id")

    from atscale.project.project import Project

    return Project(atconn=atconn, project_id=project_id)


def clone_project_dict(
    atconn: Connection,
    original_project_id: str,
    new_project_name: str,
) -> dict:
    """makes a clone of the orginal projects dictionary with a new project name

    Args:
        original_project (Project): the orginal project to make a clone of
        new_project_name (str): the name of the clone

    Returns:
        dict: the project dict of the clone
    """

    # clones the project with the given id
    url = endpoints._endpoint_design_org(atconn, f"/project/{original_project_id}/clone")
    response = atconn._submit_request(request_type=RequestType.GET, url=f"{url}")
    copy_dict = json.loads(response.content)["response"]
    copy_dict["name"] = new_project_name
    copy_dict["properties"]["caption"] = new_project_name

    # this method of adjusting the ids may not work if we swap get_datasets to pass by value
    original_project_dict = atconn._get_draft_project_dict(original_project_id)
    original_datasets = project_parser.get_datasets(original_project_dict)

    data_list = []
    for dataset in original_datasets:
        data_list.append(dataset["physical"]["connection"]["id"])
    for copy_data in copy_dict["datasets"]["data-set"]:
        copy_data["physical"]["connection"]["id"] = data_list.pop(0)

    return copy_dict


def create_dataset_columns_from_atscale_table_columns(
    table_columns: list,
) -> list:
    """Takes information about table columns as formatted by atscale and formats them for reference in a dataset specification.

    Args:
        table_columns (list): a list of table columns formatted as referenced by atscale

    Returns:
        list: a list of python dictionaries that represent table columns formatted for use in an atscale data set.
    """
    columns = []
    for name, d_type in table_columns:
        column = templates.create_column_dict(name=name, data_type=d_type)
        columns.append(column)
    return columns


def add_dataset(
    project_dict: dict,
    dataset: dict,
):
    """Adds a dataset into the provided project_dict

    Args:
        project_dict (dict): the project_dict to edit
        dataset (dict): the dataset dict to add into the project
    """
    # setdefault only sets the value if it is currently None
    project_dict["datasets"].setdefault("data-set", [])
    project_dict["datasets"]["data-set"].append(dataset)


def create_dataset(
    table_name: str,
    warehouse_id: str,
    table_columns: list,
    database: str = None,
    schema: str = None,
    dataset_name: str = None,
    allow_aggregates: bool = True,
):
    """Creates a dataset dictionary from the provided table

    Args:
        table_name (str): The name of the new dataset
        warehouse_id (str): the warehouse to look for the table in
        table_columns (list): the atscale table columns to turn into dataset columns
        database (str, optional): the database to find the table in. Defaults to None.
        schema (str, optional): the schema to find the table in. Defaults to None.
        dataset_name (str, optional): the name of the dataset to be created. Defaults to None to use table_name.
        allow_aggregates (bool, optional): Whether to allow aggregates to be built off of the dataset. Defaults to True.

    Returns:
        Tuple(dict, str): The dataset_dict and dataset_id of the created dataset
    """
    if not dataset_name:
        dataset_name = table_name
    columns = create_dataset_columns_from_atscale_table_columns(table_columns)
    dataset_id = str(uuid.uuid4())
    dataset = templates.create_dataset_dict(
        dataset_id=dataset_id,
        dataset_name=dataset_name,
        table_name=table_name,
        warehouse_id=warehouse_id,
        columns=columns,
        schema=schema,
        database=database,
        allow_aggregates=allow_aggregates,
    )
    return dataset, dataset_id


def create_query_dataset(
    name: str,
    query: str,
    columns: List[Tuple[str, str]],
    warehouse_id: str,
    allow_aggregates: bool,
):
    """Takes a name, sql expression, columns as returned by connection.get_query_columns(), and the
    warehouse_id of the connected warehouse to query against.

    Args:
        name(str): The display and query name of the dataset
        query(str): A valid SQL expression with which to directly query the warehouse of the given warehouse_id.
        columns (list): the columns from the resulting query.
        warehouse_id(str): The warehouse id of the warehouse this qds and its project are pointing at.
        allow_aggregates(bool): Whether or not aggregates should be built off of this QDS.

    Returns:
        dict: The dict to append to project_dict['datasets']['dataset']
    """
    column_dict_list = create_dataset_columns_from_atscale_table_columns(table_columns=columns)
    return templates.create_query_dataset_dict(
        dataset_id=str(uuid.uuid4()),
        dataset_name=name,
        warehouse_id=warehouse_id,
        columns=column_dict_list,
        allow_aggregates=allow_aggregates,
        query=query,
    )


def add_calculated_column_to_project_dataset(
    atconn: Connection,
    data_set: dict,
    column_name: str,
    expression: str,
    column_id: str = None,
):
    """Mutates the provided data_set by adding a calculated column based on the provided column_name and expression.

    Args:
        atconn (Connection): an AtScale connection
        data_set (dict): the data set to be mutated
        column_name (str): the name of the new calculated column
        expression (str): the sql expression that will create the values for the calculated column
        column_id (str): the id for the column. Defaults to None to generate one.
    """
    conn = data_set["physical"]["connection"]["id"]
    table = data_set["physical"]["tables"][0]
    table_name = table["name"]
    # TODO
    database = table.get("database", None)
    schema = table.get("schema", None)

    # submit a request to calculate the data type of the expression
    url = endpoints._endpoint_expression_eval(atconn, suffix=f"/conn/{conn}/table/{table_name}")
    data = {"dbschema": schema, "expression": expression, "database": database}
    response = atconn._submit_request(
        request_type=RequestType.POST,
        url=url,
        data=data,
        content_type="x-www-form-urlencoded",
    )

    resp = json.loads(response.text)
    data_type = resp["response"]["data-type"]  # TODO: test for all data-types

    new_column = templates.create_column_dict(
        name=column_name,
        expression=expression,
        data_type=data_type,
        column_id=column_id,
    )

    data_set["physical"].setdefault("columns", [])
    data_set["physical"]["columns"].append(new_column)


def _check_if_qds(
    data_set: dict,
) -> bool:
    """Checks if a data set is a qds.

    Args:
        data_set (dict): the data set to be checked

    Returns:
        bool: True if this is a qds
    """
    return len(data_set.get("physical", {}).get("queries", [])) > 0
