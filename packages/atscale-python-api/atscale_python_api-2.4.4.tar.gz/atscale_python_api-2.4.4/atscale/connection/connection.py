import getpass
import json
import logging
from typing import Dict, Optional, List, Tuple
import cryptocode
import requests
from html import unescape
import re
from atscale.base.enums import RequestType
from atscale.errors.atscale_errors import UserError, AtScaleExtrasDependencyImportError
from atscale.utils import request_utils
from atscale.utils.input_utils import choose_id_and_name_from_dict_list
from atscale.base import endpoints, templates, enums

logger = logging.getLogger(__name__)


class Connection:
    """An object responsible for the fundamental level of connection and communication to AtScale in the explicit
    realm of a user and an organization."""

    def __init__(
        self,
        server: str,
        username: str,
        password: Optional[str] = None,
        organization: Optional[str] = None,
        design_center_server_port: str = "10500",
        engine_port: str = "10502",
        jdbc_driver_class="org.apache.hive.jdbc.HiveDriver",
        jdbc_driver_path="",
    ):
        """Instantiates a Connection to an AtScale server given the associated parameters. After instantiating,
        Connection.connect() needs to be called to attempt to establish and store the connection.

        Args:
            server (str): The address of the AtScale server. Be sure to exclude any accidental / or : at the end
            username (str): The username to log in with.
            password (str, optional): The password to log in with. Leave as None to prompt upon calling connect().
            organization (str, optional): The organization id to work in. Can be set later by calling select_org()
                which will list all and prompt or set automatically if the user only has access to one organization.
            design_center_server_port (str, optional): The connection port for the design center. Defaults to 10500.
            engine_port (str, optional): The connection port for the engine. Defaults to 1502.
            jdbc_driver_class (str, optional): The class of the hive jdbc driver to use. Defaults to org.apache.hive.jdbc.HiveDriver for suggested driver.
            jdbc_driver_path (str, optional): The path to the hive jdbc driver to use. Defaults to '' which will not allow querying via jdbc
        """
        # use the setter so it can throw exception if server is None
        if len(server) > 0 and server[-1] == "/":
            server = server[:-1]
        self.session = requests.Session()
        self._server = server
        # use the setter so it can throw exception if username is None
        self.username: str = username
        if password:
            self._password = cryptocode.encrypt(password, "better than nothing")
        else:
            self._password = None
        self.jdbc_string = None
        self.jdbc_driver_path = jdbc_driver_path
        self.jdbc_driver_class = jdbc_driver_class
        self._organization: Optional[str] = organization
        self.design_center_server_port: Optional[str] = design_center_server_port
        self.engine_port: str = engine_port
        # token as private var; see: https://docs.python.org/3/tutorial/classes.html#private-variables
        self.__token: str = None

    @property
    def server(self) -> str:
        """Getter for the server instance variable

        Returns:
            str: the server string
        """
        return self._server

    @server.setter
    def server(
        self,
        value: str,
    ):
        """Setter for the server instance variable. Resets connection

        Args:
            value (str): the new server string
        """
        raise UserError("The value of server is FINAL")

    @property
    def organization(self) -> str:
        """Getter for the organization instance variable

        Returns:
            str: the organization string
        """
        return self._organization

    @organization.setter
    def organization(
        self,
        value: str,
    ):
        """Setter for the organization instance variable. Resets connection if value is None

        Args:
            value (str): the new organization string. Resets connection if None
        """
        if value is None:
            # Then they will have to (re)connect to select one.
            # I figure "no connection" errors will be easier to
            # understand than those from passing in None for org
            self.__set_token(None)
        # I don't force a reconnect otherwise. The REST API will
        # respond with errors if the user associated with token
        # Doesn't have access to the set organization.
        self._organization = value
        self._set_jdbc_string()

    @property
    def username(self) -> str:
        """Getter for the username instance variable

        Returns:
            str: the username string
        """
        return self._username

    @username.setter
    def username(
        self,
        value: str,
    ):
        """The setter for the username instance variable. Resets connection

        Args:
            value (str): the new username string
        """
        if value is None:
            raise ValueError("Must specify username.")
        # set token to none to require (re)connect
        self.__set_token(None)
        self._username = value

    @property
    def password(self) -> str:
        """The getter for the password instance variable

        Raises:
            Exception: because passwords are meant to be secure.
        """
        raise Exception("Passwords cannot be retrieved.")

    @password.setter
    def password(
        self,
        value: str,
    ):
        """The setter for the password instance variable. Resets connection

        Args:
            value (str): the new password to try
        """
        if value is None:
            raise ValueError("Must specify password.")
        # set token to none to require (re)connect
        self.__set_token(None)
        self._password = cryptocode.encrypt(value, "better than nothing")

    @property
    def design_center_server_port(self) -> str:
        """Getter for the design_center_server_port instance variable

        Returns:
            str: the username string
        """
        return self._design_center_server_port

    @design_center_server_port.setter
    def design_center_server_port(
        self,
        value: str,
    ):
        """The setter for the design_center_server_port instance variable. Resets connection

        Args:
            value (str): the new username string
        """
        if value is None:
            raise ValueError("Must specify design_center_server_port.")
        # set token to none to require (re)connect
        self.__set_token(None)
        self._design_center_server_port = value

    @property
    def engine_port(self) -> str:
        """Getter for the engine_port instance variable

        Returns:
            str: the username string
        """
        return self._engine_port

    @engine_port.setter
    def engine_port(
        self,
        value: str,
    ):
        """The setter for the engine_port instance variable. Resets connection

        Args:
            value (str): the new username string
        """
        if value is None:
            raise ValueError("Must specify engine_port.")
        # set token to none to require (re)connect
        self.__set_token(None)
        self._engine_port = value

    def __set_token(
        self,
        value,
    ):
        """Private method as a convenience for maintaining headers when the token is changed.
        See https://docs.python.org/3/tutorial/classes.html#private-variables
        Args:
            value (str): the new token value
        """
        self.__token = value

    def _set_jdbc_string(self):
        if not self.__token:
            self._auth()

        server = self.server.split("//")[1]
        org_name = [org["name"] for org in self.get_orgs() if org["id"] == self.organization][0]
        response = self._submit_request(
            request_type=RequestType.GET, url=endpoints._endpoint_jdbc_port(self)
        )
        jdbc_port = json.loads(response.content)["response"]["hiveServer2Port"]
        self.jdbc_string = f"jdbc:hive2://{server}:{jdbc_port}/{org_name};AuthMech=3"

    def _submit_request(
        self,
        request_type: RequestType,
        url: str,
        content_type: str = "json",
        data: str = "",
        raises: bool = False,
    ):
        headers = request_utils.generate_headers(content_type, self.__token)
        if request_type == RequestType.GET:
            response = request_utils.get_rest_request(
                url, data, headers, raises, session=self.session
            )
        elif request_type == RequestType.POST:
            response = request_utils.post_rest_request(
                url, data, headers, raises, session=self.session
            )
        elif request_type == RequestType.PUT:
            response = request_utils.put_rest_request(
                url, data, headers, raises, session=self.session
            )
        elif request_type == RequestType.DELETE:
            response = request_utils.delete_rest_request(
                url, data, headers, raises, session=self.session
            )
        else:
            raise Exception("Invalid request type")
        # If we get a 401 re-auth and try again else just do the normal check response flow
        if response.status_code == 401 or response.status_code == 403:
            logger.info("Token expired reauthorizing")
            self._auth()
            return self._submit_request(request_type, url, content_type, data, raises=True)
        if not response.ok and json.loads(response.text).get("response", {}).get(
            "error", ""
        ).endswith("i/o timeout"):
            logger.info("I/O internal server error, retrying")
            return self._submit_request(request_type, url, content_type, data, raises=True)
        if not raises:
            request_utils.check_response(response)
        return response

    def connect(
        self,
        organization: Optional[str] = None,
    ):
        """Connects to atscale server using class variables necessary for authentication (which can be set directly, provided in constructor,
        or passed as a parameter here). Validates the license, stores the api token, and sets the organization.
        May ask for user input.

        Args:
            organization (Optional[str], optional): The organization to connect to. Defaults to None.
        """
        # if not self.password:
        #     self.password = getpass.getpass(prompt=f'Please enter your AtScale password for user \'{self.username}\': ')
        if organization is not None:
            self.organization = organization

        if self.organization is None:
            # This can still assign none to the org, in which case token will be
            # set to None in the setter for organization, and therefore this method
            # will exit but stil no token, connected() returns false. I figured those
            # errors will be easier to understand than those from passing None for org to urls
            self._select_org_pre_auth()
        self._auth()
        self._validate_license()
        self._set_jdbc_string()

    def _auth(self):
        # https://documentation.atscale.com/2022.1.0/api/authentication
        header = request_utils.generate_headers()
        url = endpoints._endpoint_auth_bearer(self)
        if self._password:
            password = cryptocode.decrypt(self._password, "better than nothing")
        else:
            password = getpass.getpass(
                prompt=f"Please enter your AtScale password for user '{self.username}': "
            )
            self._password = cryptocode.encrypt(password, "better than nothing")

        response = self.session.get(
            url,
            headers=header,
            auth=requests.auth.HTTPBasicAuth(self.username, password),
            stream=False,
        )
        if response.ok:
            self.__set_token(response.content.decode())
        elif response.status_code == 401:
            self._password = None
            raise UserError(response.text)
        else:
            self._password = None
            resp = json.loads(response.text)
            raise Exception(resp["response"]["error"])

    def _validate_license(
        self,
        specific_feature_flag=None,
    ) -> bool:
        """Validates that the AtScale server has the necessary flags in its license.

        Args:
            specific_feature_flag (Optional[str], optional): The specific feature flag to validate. Defaults to None to check all flags necessary for AI-Link.
        """
        response = self._submit_request(
            request_type=RequestType.GET, url=endpoints._endpoint_engine_version(self)
        )
        engine_version_string = response.text
        engine_version = float(
            engine_version_string.split(".")[0] + "." + engine_version_string.split(".")[1]
        )
        response = self._submit_request(
            request_type=RequestType.GET, url=endpoints._endpoint_license_details(self)
        )
        resp = json.loads(response.text)
        if not specific_feature_flag:
            if (
                "query_rest" not in resp["response"]["content"]["features"]
                or resp["response"]["content"]["features"]["query_rest"] is False
            ):
                logger.warning(
                    "Query REST Endpoint not licensed for your server. You will be unable to query through AI-Link"
                )
            if engine_version >= 2022.2:
                if (
                    "data_catalog_api" not in resp["response"]["content"]["features"]
                    or resp["response"]["content"]["features"]["data_catalog_api"] is False
                ):
                    logger.warning(
                        "Data Catalog not licensed for your server. You may have issues pulling metadata"
                    )
            if (
                "ai-link" not in resp["response"]["content"]["features"]
                or resp["response"]["content"]["features"]["ai-link"] is False
            ):
                self.__set_token(None)
                raise Exception("AI-Link not licensed for your AtScale server")
            return True
        else:
            if (
                specific_feature_flag not in resp["response"]["content"]["features"]
                or resp["response"]["content"]["features"][specific_feature_flag] is False
            ):
                return False
            else:
                return True

    def connected(self) -> bool:
        """Convenience method to determine if this object has connected to the server and authenticated.
        This is determined based on whether a token has been stored locally after a connection with the
        server.

        Returns:
            boolean: whether this object has connected to the server and authenticated.
        """
        if self.__token is not None:
            return True
        else:
            return False

    def get_orgs(self) -> List[dict]:
        """Get a list of metadata for all organizations available to the connection.

        Returns:
            list(dict): a list of dictionaries providing metadata per organization
        """
        self._check_connected()

        # The current API docs are a bit off in the response descriptions so leaving out of docstring
        # https://documentation.atscale.com/2022.1.0/api-ref/organizations
        # url = f'{self.server}:{self.design_center_server_port}/api/1.0/org'
        # submit request, check for errors which will raise exceptions if there are any
        # response = self._submit_request(request_type=RequestType.GET, url=url)
        # if we get down here, no exceptions raised, so parse response
        # return json.loads(response.content)['response']

        # Due to engien bug requiring sysadmin for above endpoint we need to use the below function.
        # This is a workaround and should be removed when the endpoint is fixed
        return self._get_orgs_for_all_users()

    def _get_orgs_for_all_users(self):
        url = endpoints._endpoint_login_screen(self)
        resp = self._submit_request(request_type=RequestType.GET, url=url)
        match = re.search("window\.organizations = (.*?]);", str(resp.content))
        match = match[1]
        match = unescape(match).encode("utf-8").decode("unicode_escape")
        org_list = json.loads(match)
        return org_list

    def select_org(self):
        """Uses an established connection to enable the user to select from the orgs they have access to.
        This is different from setting the organization directly, for which there is a property and associated
        setter.

        Raises:
            UserError: error if there is no connection already established
        """
        orgs = self.get_orgs()

        org = choose_id_and_name_from_dict_list(orgs, "Please choose an organization:")
        if org is not None:
            self.organization = org["id"]

    def _select_org_pre_auth(self):
        """Same as select_org but will list all organizations regardless of user access"""
        orgs = self._get_orgs_for_all_users()
        org = choose_id_and_name_from_dict_list(dcts=orgs, prompt="Please choose an organization:")
        if org is not None:
            self.organization = org["id"]
        else:
            raise UserError("An organization must be selected before authentication occurs.")

    def _get_connection_groups(self) -> list:
        u = endpoints._endpoint_connection_groups(self)
        # this call will handle or raise any errors
        tmp = self._submit_request(request_type=RequestType.GET, url=u)
        # bunch of parsing I'm just going to wrap in a try and if any o fit fails I'll log and raise
        try:
            content = json.loads(tmp.content)
            if content["response"]["results"].setdefault("count", 0) < 1:
                raise UserError("No connection groups found")
            return content["response"]["results"]["values"]
        except UserError as err:
            logger.exception("no connection groups found in _get_connection_groups")
            raise
        except:
            logger.exception("couldn't parse connection groups")
            raise Exception("Error encountered while parsing connection groups.")

    def _get_published_projects(self):
        url = endpoints._endpoint_published_project_list(self)
        # submit request, check for errors which will raise exceptions if there are any
        response = self._submit_request(request_type=RequestType.GET, url=url)
        # if we get down here, no exceptions raised, so parse response
        return json.loads(response.content)["response"]

    def _get_projects(self):
        """See https://documentation.atscale.com/2022.1.0/api-ref/projects#projects-list-all
        Grabs projects using organiation information this object was initialized with. I believe this
        will only return unpublished projects since it indicates full json is returned and that doesn't
        happen with published projects.

        Raises:
            Exception:

        Returns:
            json: full json spec of any projects
        """
        # construct the request url
        url = endpoints._endpoint_list_projects(self)
        # submit request, check for errors which will raise exceptions if there are any
        response = self._submit_request(request_type=RequestType.GET, url=url)
        # if we get down here, no exceptions raised, so parse response
        resp = json.loads(response.content)["response"]
        return resp

    def _get_draft_project_dict(
        self,
        draft_project_id: str,
    ) -> dict:
        """Get the draft project json and convert to a dict.

        Args:
            draft_project_id (str): The id for the draft project (i.e. not published project) to be retrieved.

        Raises:
            UserError: If there is no connection this error will be raised.
            Exception: If there is some other problem communicating with the atscale instance an exception may be raised

        Returns:
            dict: the dict representation of the draft project, or None if no project exists for the provided draft_project_id
        """
        # construct the request url
        url = endpoints._endpoint_design_org(self, f"/project/{draft_project_id}")
        response = self._submit_request(request_type=RequestType.GET, url=url)
        return json.loads(response.content)["response"]

    # hitting endpoints

    def _post_atscale_query(
        self,
        query,
        project_name,
        use_aggs=True,
        gen_aggs=False,
        fake_results=False,
        use_local_cache=True,
        use_aggregate_cache=True,
        timeout=10,
    ):
        """Submits an AtScale SQL query to the AtScale server and returns the http requests.response object.

        :param str query: The query to submit.
        :param bool use_aggs: Whether to allow the query to use aggs. Defaults to True.
        :param bool gen_aggs: Whether to allow the query to generate aggs. Defaults to False.
        :param bool fake_results: Whether to use fake results. Defaults to False.
        :param bool use_local_cache: Whether to allow the query to use the local cache. Defaults to True.
        :param bool use_aggregate_cache: Whether to allow the query to use the aggregate cache. Defaults to True.
        :param int timeout: The number of minutes to wait for a response before timing out. Defaults to 10.
        :return: A response with a status code, text, and content fields.
        :rtype: requests.response
        """
        json_data = json.dumps(
            templates.create_query_for_post_request(
                query=query,
                project_name=project_name,
                organization=self.organization,
                use_aggs=use_aggs,
                gen_aggs=gen_aggs,
                fake_results=fake_results,
                use_local_cache=use_local_cache,
                use_aggregate_cache=use_aggregate_cache,
                timeout=timeout,
            )
        )
        response = self._submit_request(
            request_type=RequestType.POST,
            url=endpoints._endpoint_atscale_query(self, "/submit"),
            data=json_data,
        )
        return response

    def get_jdbc_connection(self):
        """Returns a jaydebeapi connection to the data model

        Raises:
            UserError: If jdbc_driver_path is not set.

        Returns:
            Connection: The jaydebeapi connection
        """
        try:
            import jaydebeapi
        except ImportError as e:
            raise AtScaleExtrasDependencyImportError("jdbc", str(e))

        if self.jdbc_driver_path == "":
            raise UserError("Cannot create jdbc connection because jdbc_driver_path is not set")
        return jaydebeapi.connect(
            self.jdbc_driver_class,
            self.jdbc_string,
            [self.username, cryptocode.decrypt(self._password, "better than nothing")],
            self.jdbc_driver_path,
        )

    def get_connected_warehouses(self) -> List[Dict]:
        """Returns metadata on all warehouses visible to the connection

        Raises:
            UserError: If no connection established.

        Returns:
            List[Dict]: The list of available warehouses
        """
        self._check_connected()

        connectionGroups = self._get_connection_groups()

        output_list = []
        result_keys = ["name", "platformType", "connectionId"]
        result_key_map = {
            "name": "name",
            "platformType": "platform",
            "connectionId": "warehouse_id",
        }

        for warehouse in connectionGroups:
            output_list.append(
                {result_key_map[res_key]: warehouse[res_key] for res_key in result_keys}
            )
        return output_list

    def _get_warehouse_platform(
        self,
        warehouse_id: str,
    ) -> enums.PlatformType:
        self._check_connected()
        warehouses = self.get_connected_warehouses()
        warehouse = [w for w in warehouses if w["warehouse_id"] == warehouse_id]  # single item list
        if len(warehouse) == 0:
            raise Exception(
                f"No warehouse exists in the connection with the warehouse_id '{warehouse_id}'. "
                f"The following warehouses are present: {warehouses}"
            )
        warehouse = warehouse[
            0
        ]  # warehouse ids are unique so we should have gotten a list of length 1
        return enums.PlatformType(warehouse["platform"])

    def get_connected_databases(
        self,
        warehouse_id: str,
    ) -> List[str]:
        """Get a list of databases the organization can access in the provided warehouse.

        Args:
            warehouse_id (str): The atscale warehouse connection to use.

        Returns:
            List[str]: The list of available databases
        """

        self._check_connected()

        # decided only make a dedicated endpoint in endpoints.py if it wouldn't require add parameters
        u = endpoints._endpoint_warehouse(self, f"/conn/{warehouse_id}/tables/cacheRefresh")
        response = self._submit_request(request_type=RequestType.POST, url=u, data="")

        u = endpoints._endpoint_warehouse(self, f"/conn/{warehouse_id}/databases")
        response = self._submit_request(request_type=RequestType.GET, url=u)
        return json.loads(response.content)["response"]

    def get_connected_schemas(
        self,
        warehouse_id: str,
        database: str,
    ) -> List[str]:
        """Get a list of schemas the organization can access in the provided warehouse and database.

        Args:
            warehouse_id (str): The atscale warehouse connection to use.
            database (str): The database to use.

        Returns:
            List[str]: The list of available tables
        """

        self._check_connected()

        u = endpoints._endpoint_warehouse(self, f"/conn/{warehouse_id}/tables/cacheRefresh")
        response = self._submit_request(request_type=RequestType.POST, url=u, data="")

        info = f"?database={database}"
        u = endpoints._endpoint_warehouse(self, f"/conn/{warehouse_id}/schemas{info}")
        response = self._submit_request(request_type=RequestType.GET, url=u)
        return json.loads(response.content)["response"]

    def get_connected_tables(
        self,
        warehouse_id: str,
        database: str,
        schema: str,
    ) -> List[str]:
        """Get a list of tables the organization can access in the provided warehouse, database, and schema.

        Args:
            warehouse_id (str): The atscale warehouse connection to use.
            database (str): The database to use.
            schema (str,): The schema to use.

        Returns:
            List[str]: The list of available tables
        """

        self._check_connected()

        u = endpoints._endpoint_warehouse(self, f"/conn/{warehouse_id}/tables/cacheRefresh")
        response = self._submit_request(request_type=RequestType.POST, url=u, data="")

        info = f"?database={database}&schema={schema}"
        u = endpoints._endpoint_warehouse(self, f"/conn/{warehouse_id}/tables{info}")
        response = self._submit_request(request_type=RequestType.GET, url=u)
        return json.loads(response.content)["response"]

    def get_query_columns(
        self,
        warehouse_id: str,
        query: str,
    ):
        """Get all columns of a direct query, to the given warehouse_id, as they are represented by AtScale.

        Args:
            warehouse_id (str): The atscale warehouse to use.
            query (str): A valid query for the warehouse of the given id, of which to return the resulting columns

        Returns:
            List[Tuple]: A list of columns represented as Tuples of (name, data-type)
        """
        self._check_connected()

        # cache refresh
        u = endpoints._endpoint_warehouse(self, f"/conn/{warehouse_id}/tables/cacheRefresh")
        self._submit_request(request_type=RequestType.POST, url=u)

        # preview query
        url = endpoints._endpoint_warehouse(self, f"/conn/{warehouse_id}/query/info")
        payload = {"query": query}
        response = self._submit_request(
            request_type=RequestType.POST, url=url, data=json.dumps(payload)
        )
        # parse response into tuples of name and data-type
        columns = [
            (x["name"], x["column-type"]["data-type"])
            for x in json.loads(response.content)["response"]["columns"]
        ]
        return columns

    def get_table_columns(
        self,
        warehouse_id: str,
        table_name: str,
        database: str = None,
        schema: str = None,
        expected_columns: List[str] = None,
    ) -> List[Tuple]:
        """Get all columns in a given table

        Args:
            warehouse_id (str): The atscale warehouse to use.
            table_name (str): The name of the table to use.
            database (str, optional): The database to use. Defaults to None to use default database
            schema (str, optional): The schema to use. Defaults to None to use default schema
            expected_columns (List[str], optional): A list of expected column names to validate. Defaults to None

        Returns:
             List[Tuple]: Pairs of the columns and data-types (respectively) of the passed table
        """
        self._check_connected()

        u = endpoints._endpoint_warehouse(self, f"/conn/{warehouse_id}/tables/cacheRefresh")
        self._submit_request(request_type=RequestType.POST, url=u, data="")

        url = endpoints._endpoint_warehouse(self, f"/conn/{warehouse_id}/table/{table_name}/info")
        if database:
            url += f"?database={database}"
            if schema:
                url += f"&schema={schema}"
        elif schema:
            url += f"?schema={schema}"
        response = self._submit_request(request_type=RequestType.GET, url=url)
        table_columns = [
            (x["name"], x["column-type"]["data-type"])
            for x in json.loads(response.content)["response"]["columns"]
        ]
        table_column_names = [x[0] for x in table_columns]
        if expected_columns is not None:
            for column in expected_columns:
                if column in table_column_names:
                    continue
                elif column.upper() in table_column_names:
                    logging.warn(f"Column name: {column} appears as {column.upper()}")
                elif column.lower() in table_column_names:
                    logging.warn(f"Column name: {column} appears as {column.lower()}")
                else:
                    logging.warn(f"Column name: {column} does not appear in table {table_name}")
        return table_columns

    def _unpublish_project(
        self,
        published_project_id: str,
    ) -> bool:
        """Internal function to unpublishes the provided published_project_id making in no longer queryable

        Args:
            published_project_id (str): the id of the published project to unpublish

        Returns:
            bool: Whether the unpublish was successful
        """
        u = endpoints._endpoint_unpublished_project(self, f"/schema/{published_project_id}")
        response = self._submit_request(request_type=RequestType.DELETE, url=u)
        if response.status_code == 200:
            return True
        else:
            logger.error(json.loads(response.content)["response"]["status"]["message"])
            return False

    def _check_connected(
        self,
        err_msg=None,
    ):
        outbound_error = "Please establish a connection by calling connect() first."
        if err_msg:
            outbound_error = err_msg
        if not self.connected():
            raise UserError(outbound_error)
