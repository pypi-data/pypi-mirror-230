from pandas import DataFrame
import cryptocode
import getpass
import inspect
import logging

from atscale.errors import atscale_errors
from atscale.errors.atscale_errors import AtScaleExtrasDependencyImportError
from atscale.db.sqlalchemy_connection import SQLAlchemyConnection
from atscale.base.enums import (
    PlatformType,
    PandasTableExistsActionType,
    PysparkTableExistsActionType,
)
from atscale.utils import validation_utils

logger = logging.getLogger(__name__)


class Databricks(SQLAlchemyConnection):
    """The child class of SQLConnection whose implementation is meant to handle
    interactions with Databricks.
    """

    platform_type: PlatformType = PlatformType.DATABRICKS

    conversion_dict = {
        "<class 'numpy.int32'>": "INT",
        "<class 'numpy.int64'>": "BIGINT",
        "<class 'numpy.uint64'>": "BIGINT",
        "<class 'numpy.float64'>": "DOUBLE",
        "<class 'str'>": "STRING",
        "<class 'numpy.bool_'>": "BOOLEAN",
        "<class 'pandas._libs.tslibs.timestamps.Timestamp'>": "TIMESTAMP",
        "<class 'datetime.date'>": "DATE",
        "<class 'decimal.Decimal'>": "DECIMAL",
        "<class 'numpy.datetime64'>": "TIMESTAMP",
    }

    def __init__(
        self,
        host: str,
        catalog: str,
        schema: str,
        http_path: str,
        token: str = None,
        port: int = 443,
        warehouse_id: str = None,
    ):
        """Constructs an instance of the Databricks SQLConnection. Takes arguments necessary to find the host
            and schema. Since prompting login is not viable, this requires an authorization token.

        Args:
            host (str): The host of the intended Databricks connections
            catalog (str): The catalog of the intended Databricks connections
            schema (str): The schema of the intended Databricks connections
            http_path (str): The web path of the intended Databricks connections
            token (str, optional): The authorization token needed to interact with Databricks. Will prompt if None
            port (int, optional): A port for the connection. Defaults to 443.
            warehouse_id (str, optional): The AtScale warehouse id to automatically associate the connection with if writing tables. Defaults to None.
        """

        try:
            from sqlalchemy import create_engine
            from databricks import sql
        except ImportError as e:
            raise AtScaleExtrasDependencyImportError("databricks", str(e))

        super().__init__(warehouse_id)

        # ensure any builder didn't pass any required parameters as None
        local_vars = locals()
        inspection = inspect.getfullargspec(self.__init__)
        validation_utils.validate_required_params_not_none(
            local_vars=local_vars, inspection=inspection
        )

        if token:
            self._token = cryptocode.encrypt(token, self.platform_type.value)
        else:
            self._token = None
        self._host = host
        self._catalog = catalog
        self._schema = schema
        self._http_path = http_path
        self._port = port
        try:
            validation_connection = self.engine.connect()
            validation_connection.close()
            self.dispose_engine()
        except:
            logger.error("Unable to create database connection, please verify the inputs")
            raise

    @property
    def token(self) -> str:
        raise Exception("Token cannot be retrieved.")

    @token.setter
    def token(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._token = cryptocode.encrypt(value, self.platform_type.value)
        self.dispose_engine()

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._host = value
        self.dispose_engine()

    @property
    def catalog(self) -> str:
        return self._catalog

    @catalog.setter
    def catalog(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._catalog = value
        self.dispose_engine()

    @property
    def schema(self) -> str:
        return self._schema

    @schema.setter
    def schema(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._schema = value
        self.dispose_engine()

    @property
    def http_path(self) -> str:
        return self._http_path

    @http_path.setter
    def http_path(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._http_path = value
        self.dispose_engine()

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._port = value
        self.dispose_engine()

    @property
    def _database(self):
        return self._catalog

    def clear_auth(self):
        """Clears any authentication information, like password or token from the connection."""
        self._token = None
        self.dispose_engine()

    def _get_connection_url(self):
        from sqlalchemy.engine import URL

        if not self._token:
            self._token = cryptocode.encrypt(
                getpass.getpass(prompt="Please enter your Databricks token: "),
                self.platform_type.value,
            )
        token = cryptocode.decrypt(self._token, self.platform_type.value)
        connection_url = URL.create(
            "databricks+connector",
            username="token",
            password=token,
            host=self._host,
            port=self._port,
            database=self._catalog,
        )
        return connection_url

    def _get_connection_parameters(self):
        parameters = {"http_path": self._http_path}
        return parameters

    @staticmethod
    def _format_types(
        dataframe: DataFrame,
    ) -> dict:
        types = {}
        for i in dataframe.columns:
            if (
                str(type(dataframe[i].loc[~dataframe[i].isnull()].iloc[0]))
                in Databricks.conversion_dict
            ):
                types[i] = Databricks.conversion_dict[
                    str(type(dataframe[i].loc[~dataframe[i].isnull()].iloc[0]))
                ]
            else:
                types[i] = Databricks.conversion_dict["<class 'str'>"]
        return types

    def _create_table(
        self,
        table_name: str,
        types: dict,
        cursor,
    ):
        # If the table exists we'll just let this fail and raise the appropriate exception.
        # Related checking to handle gracefully is within calling methods.

        if not cursor.tables(table_name=table_name, table_types=["TABLE"]).fetchone():
            operation = "CREATE TABLE `{}`.`{}`.`{}` (".format(
                self.catalog, self.schema, table_name
            )
            for key, value in types.items():
                operation += "`{}` {}, ".format(key, value)
            operation = operation[:-2]
            operation += ")"
            cursor.execute(operation)
            # autocommit should be on by default

    def write_df_to_db(
        self,
        table_name: str,
        dataframe: DataFrame,
        if_exists: PandasTableExistsActionType = PandasTableExistsActionType.FAIL,
        chunksize: int = 1000,
    ):
        # validate the non-null inputs
        validation_utils.validate_required_params_not_none(
            local_vars=locals(),
            inspection=inspect.getfullargspec(self.write_df_to_db),
        )
        from databricks import sql

        connection = sql.connect(
            server_hostname=self._host,
            http_path=self._http_path,
            access_token=cryptocode.decrypt(self._token, self.platform_type.value),
        )
        cursor = connection.cursor()

        if cursor.tables(
            table_name=table_name, schema_name=self.schema, catalog_name=self.catalog
        ).fetchone():
            exists = True
        else:
            exists = False

        if exists and if_exists == PandasTableExistsActionType.FAIL:
            raise Exception(
                f"A table named: {table_name} already exists in schema: {self.schema} for catalog: {self.catalog}"
            )

        types = self._format_types(dataframe)

        if exists and if_exists == PandasTableExistsActionType.REPLACE:
            operation = f"DROP TABLE `{self.catalog}`.`{self.schema}`.`{table_name}`"
            cursor.execute(operation)
            self._create_table(table_name, types, cursor)
        elif not exists:
            self._create_table(table_name, types, cursor)

        # add in break characters
        for key, value in types.items():
            if "STRING" in value:
                dataframe[key] = dataframe[key].str.replace(r"'", r"\'")

        operation = f"INSERT INTO `{self.catalog}`.`{self.schema}`.`{table_name}` VALUES ("

        list_df = [dataframe[i : i + chunksize] for i in range(0, dataframe.shape[0], chunksize)]
        for df in list_df:
            op_copy = operation
            for index, row in df.iterrows():
                for col in df.columns:
                    if "STRING" in types[col] or "DATE" in types[col] or "TIMESTAMP" in types[col]:
                        op_copy += "'{}', ".format(row[col])
                    else:
                        op_copy += f"{row[col]}, ".replace("nan", "null")
                op_copy = op_copy[:-2]
                op_copy += "), ("
            op_copy = op_copy[:-3]
            cursor.execute(op_copy)
        # adding close of cursor which I didn't see before
        cursor.close()
        connection.close()

    def _write_pysparkdf_to_spark_db(
        self,
        pyspark_dataframe,
        table_name: str,
        alt_database_path: str = None,
        if_exists: PysparkTableExistsActionType = PysparkTableExistsActionType.ERROR,
    ):
        """Writes the provided pyspark DataFrame into the provided table name via standard spark sql operation. Can pass in if_exists to indicate the intended behavior if
            the provided table name is already taken.

        Args:
            pyspark_dataframe (pyspark.sql.DataFrame): The pyspark dataframe to write
            table_name (str): What table to write the dataframe into
            alt_database_path (str, optional): The alternate database path to use. Will be added as a prefix to the tablename.
                Defaults to None, and uses catalog and schema. Include the trailing delimiter to go between path and tablename.
            if_exists (PysparkTableExistsActionType, optional): The intended behavior in case of table name collisions.
                Defaults to PysparkTableExistsActionType.ERROR.
        """
        try:
            from pyspark.sql import SparkSession
        except ImportError as e:
            raise atscale_errors.AtScaleExtrasDependencyImportError("jdbc", str(e))

        if alt_database_path is not None:
            table_name = alt_database_path + table_name
        else:
            table_name = f"{self.catalog}.{self.schema}.{table_name}"
        pyspark_dataframe.write.mode(if_exists.value).saveAsTable(table_name)

    def _read_pysparkdf_from_spark_db(
        self,
        spark_session,
        query: str,
    ):
        """Writes the provided pyspark DataFrame into the provided table name via standard spark sql operation. Can pass in if_exists to indicate the intended behavior if
            the provided table name is already taken.

        Args:
            spark_session (pyspark.sql.SparkSession): The pyspark SparkSession to execute the query with
            query (str): the string
        """
        try:
            from pyspark.sql import SparkSession
            from pyspark.sql.utils import AnalysisException

        except ImportError as e:
            raise atscale_errors.AtScaleExtrasDependencyImportError("spark", str(e))

        # record the defaults so that we can revert after our operation
        default_catalog = spark_session.catalog.currentCatalog()
        default_database = spark_session.catalog.currentDatabase()

        # going to throw all of these in individual try catches
        try:
            spark_session.catalog.setCurrentCatalog(self.catalog)
        except AnalysisException:
            logger.error(
                f"Unable to set default catalog to {self.catalog}, please verify the catalog of the databricks object"
            )
            raise

        try:
            spark_session.catalog.setCurrentDatabase(self.schema)
        except AnalysisException:
            spark_session.catalog.setCurrentCatalog(default_catalog)
            logger.error(
                f"Unable to set default database to {self.schema}, please verify the schema of the databricks object"
            )
            raise

        try:
            ret_df = spark_session.sql(query)
        except Exception as e:
            raise e
        finally:
            spark_session.catalog.setCurrentCatalog(default_catalog)
            spark_session.catalog.setCurrentDatabase(default_database)

        return ret_df

    def _create_table_path(
        self,
        table_name: str,
    ) -> str:
        """generates a full table file path using instance variables.

        Args:
            table_name (str): the table name to append

        Returns:
            str: the queriable location of the table
        """
        return f"{self.catalog}.{self.schema}.{table_name}"
