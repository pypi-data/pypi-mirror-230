import logging
from typing import List, Tuple, Dict, Union, Set, Optional, Any
from atscale.connection.connection import Connection
from atscale.db.sql_connection import SQLConnection
from atscale.db.connections import (
    bigquery,
    databricks,
    iris,
    mssql,
    redshift,
    snowflake,
    synapse,
)
from atscale.errors import atscale_errors
from atscale.base import enums


def enum_to_dbconn(
    platform_type: enums.PlatformType,
) -> SQLConnection:
    """takes enums.PlatformType enum and returns an uninstantiated object of the associated SQLConnection class"""
    mapping = {
        enums.PlatformType.GBQ: bigquery.BigQuery,
        enums.PlatformType.DATABRICKS: databricks.Databricks,
        enums.PlatformType.IRIS: iris.Iris,
        enums.PlatformType.MSSQL: mssql.MSSQL,
        enums.PlatformType.REDSHIFT: redshift.Redshift,
        enums.PlatformType.SNOWFLAKE: snowflake.Snowflake,
        enums.PlatformType.SYNAPSE: synapse.Synapse,
    }
    return mapping[platform_type]


def get_atscale_tablename(
    atconn: Connection,
    warehouse_id: str,
    database: str,
    schema: str,
    table_name: str,
) -> str:
    """Determines the tablename as referenced by AtScale.

    Args:
        atconn (Connection):  The AtScale connection to use
        warehouse_id (str): The id in AtScale of the data warehouse to use
        database (str): The name of the database for the table
        schema (str): The name of the schema for the table
        table_name (str): The name of the table

    Raises:
        atscale_errors.UserError: If Atscale is unable to find the table this error will be raised

    Returns:
        str: The name AtScale shows for the table
    """
    atscale_tables = atconn.get_connected_tables(warehouse_id, database, schema)
    atscale_name: str = _convert_name_to_alias(
        name=table_name,
        aliases=atscale_tables,
        warning_message="Table name: {} appears as {}",
    )
    if atscale_name is None:
        raise atscale_errors.UserError(
            f"Unable to find table: {table_name}. If the table exists make sure AtScale has access to it"
        )
    return atscale_name


def get_database_and_schema(
    dbconn: SQLConnection,
) -> Tuple[str, str]:
    """Returns a tuple of the (database property, schema property) of the sqlconn object. For those objects that don't natively
    have those properties, a private property was created that maps the native terminology to database and schema

    Args:
        dbconn (SQLConnection): The connection object to get properies from

    Returns:
        Tuple[str, str]: the (database, schema)
    """
    return dbconn._database, dbconn._schema


def get_column_dict(
    atconn: Connection,
    dbconn: SQLConnection,
    warehouse_id: str,
    atscale_table_name: str,
    dataframe_columns: List[str],
) -> Dict:
    """Grabs columns from the AtScale table corresponding to the dataframe and compares columns from each, returning a dict where the
    keys are column names from the dataframe and the values are the column names as they appear in the atscale_table_name.

    Args:
        atconn (Connection):  The AtScale connection to use
        dbconn (SQLConnection): The sql connection to use to connect to interact with the data warehouse. Primary used here to get any database and schema references for the connection.
        warehouse_id (str): The id of the warehouse for AtScale to use to reach the new table
        atscale_table_name (str): the name of the table in the data warehouse as recognized by atscale that corresponds to the dataframe
        dataframe_columns (List[str]): the DataFrame columns that corresponds to the atscale_table_name

    Raises:
        atscale_errors.UserError: Potential error if the dataframe features columns that are not found within the table referenced by atscale_table_name
    Returns:
        Dict: a Dict object where keys are the column names within the dataframe and the values are the columns as they appear in atscale_table_name as seen by AtScale.
    """

    database, schema = get_database_and_schema(dbconn=dbconn)
    atscale_columns = [
        c[0]
        for c in atconn.get_table_columns(
            warehouse_id=warehouse_id,
            table_name=atscale_table_name,
            database=database,
            schema=schema,
            expected_columns=dataframe_columns,
        )
    ]
    column_dict = {}
    missing_columns = []
    # iterate over the dataframe columns, looking for near matches to accomodate databases auto capitalizing names
    proper_columns: List[str] = dataframe_columns.copy()
    proper_columns, missing_columns = _convert_names_to_atscale_names(
        names=proper_columns,
        aliases=atscale_columns,
        warning_message="Column name: {} appears as {}",
    )
    if missing_columns:
        raise atscale_errors.UserError(
            f"Unable to find columns: {missing_columns} in table: {atscale_table_name}."
        )
    column_dict = {original: proper for original, proper in zip(dataframe_columns, proper_columns)}

    return column_dict


def _get_key_cols(
    dbconn: SQLConnection,
    key_dict: dict,
):
    """If the provided key_dict requires a multi-column key (or has a key different from then value), then
        run a query to get the contents of the other join columns.

    Args:
        dbconn (SQLConnection): The connection object to query if necessary
        key_dict (dict): The dictionary describing the necessary key columns

    Returns:
        dataframe (pd.DataFrame): The additional columns information needed for the join
    """
    # check the keys for the feature. If there are more than one or only one and it doesn't match the value we will need to pull in the columns we don't have
    if len(key_dict["key_cols"]) > 1 or key_dict["key_cols"][0] != key_dict["value_col"]:
        # if it is a qds we need to select from the query
        if key_dict["query"]:
            table = f'({key_dict["query"]})'
        # if not we want to build the fully qualified table name
        else:
            table = f'{dbconn._column_quote()}{key_dict["table_name"]}{dbconn._column_quote()}'
            if key_dict["schema"]:
                table = (
                    f'{dbconn._column_quote()}{key_dict["schema"]}{dbconn._column_quote()}.{table}'
                )
            if key_dict["database"]:
                table = f'{dbconn._column_quote()}{key_dict["database"]}{dbconn._column_quote()}.{table}'
        needed_cols = key_dict["key_cols"]
        # the value column may or may not be one of the keys so add it if it is missing
        if key_dict["value_col"] not in needed_cols:
            needed_cols.append(key_dict["value_col"])
        column_string = f"{dbconn._column_quote()}, {dbconn._column_quote()}".join(needed_cols)
        query = f"SELECT DISTINCT {dbconn._column_quote()}{column_string}{dbconn._column_quote()} FROM {table}"
        df_key = dbconn.submit_query(query)
        df_key.columns = needed_cols
        return df_key
    return None


def _convert_name_to_alias(
    name: str,
    aliases: Union[List[str], Dict[str, Any], Set[str]],
    warning_message: str = None,
) -> Optional[str]:
    """Returns the converted name or its original form if it doesn't exist in the list of aliases"""
    actual, missing = _convert_names_to_atscale_names(
        names=[name], aliases=aliases, warning_message=warning_message
    )
    return actual[0]


def _convert_names_to_atscale_names(
    names: List[str],
    aliases: Union[List[str], Dict[str, Any], Set[str]],
    warning_message: str = None,
) -> Tuple[List[str], List[str]]:
    """Returns a tuple of converted (if possible) names to aliases as well as the sublist of items that do not exist
    in the aliases parameter either as is or upper or lower cased."""
    names = names.copy()
    aliases = set(aliases)  # convert to a set for constant time lookups
    missing_names = []
    for i, original_name in enumerate(names):
        if original_name in aliases:
            continue
        else:
            for fixed_name in [original_name.upper(), original_name.lower()]:
                if fixed_name in aliases:
                    names[i] = fixed_name
                    if warning_message is not None:
                        logging.warning(warning_message.format(original_name, fixed_name))
                    break
            else:  # this means if the for loop never hit the break statement
                missing_names.append(original_name)
    return names, missing_names
