### engine side endpoints
def _endpoint_connection_groups(
    atconn,
) -> str:
    return f"{atconn.server}:{atconn.engine_port}/connection-groups/orgId/{atconn.organization}"


def _endpoint_published_project_list(
    atconn,
    suffix: str = "",
):
    return f"{atconn.server}:{atconn.engine_port}/projects/published/orgId/{atconn.organization}{suffix}"


def _endpoint_unpublished_project(
    atconn,
    suffix: str = "",
):
    return f"{atconn.server}:{atconn.engine_port}/projects/orgId/{atconn.organization}{suffix}"


def _endpoint_query_view(
    atconn,
    suffix: str = "",
    limit: int = 21,
):
    """Returns the query viewing endpoint with the suffix appended"""
    return (
        f"{atconn.server}:{atconn.engine_port}/queries/orgId/{atconn.organization}"
        f"?limit={limit}&userId={atconn.username}{suffix}"
    )


def _endpoint_warehouse(
    atconn,
    suffix: str = "",
):
    """<server>:<engine_port>/data-sources/ordId/<organization>"""
    return f"{atconn.server}:{atconn.engine_port}/data-sources/orgId/{atconn.organization}{suffix}"


def _endpoint_expression_eval(
    atconn,
    suffix: str,
):
    return f"{atconn.server}:{atconn.engine_port}/expression-evaluator/evaluate/orgId/{atconn.organization}{suffix}"


def _endpoint_mdx_syntax_validation(
    atconn,
):
    return f"{atconn.server}:{atconn.engine_port}/mdx-expression/value/validate"


def _endpoint_dmv_query(
    atconn,
    suffix: str = "",
):
    return f"{atconn.server}:{atconn.engine_port}/xmla/{atconn.organization}{suffix}"


def _endpoint_jdbc_port(
    atconn,
    suffix: str = "",
):
    """Gets the jdbc port for the org"""
    return (
        f"{atconn.server}:{atconn.engine_port}/organizations/orgId/{atconn._organization}{suffix}"
    )


def _endpoint_engine_version(
    atconn,
    suffix: str = "",
):
    """Gets the version of the atscale instance"""
    return f"{atconn.server}:{atconn.engine_port}/version{suffix}"


def _endpoint_license_details(
    atconn,
    suffix: str = "",
):
    """Gets the license for this instance"""
    return f"{atconn.server}:{atconn.engine_port}/license/capabilities"


def _endpoint_atscale_query(
    atconn,
    suffix: str = "",
):
    """Sends an atscale query"""
    return f"{atconn.server}:{atconn.engine_port}/query/orgId/{atconn.organization}{suffix}"


### design center endpoints
def _endpoint_design_org(
    atconn,
    suffix: str = "",
):
    return f"{atconn.server}:{atconn.design_center_server_port}/api/1.0/org/{atconn.organization}{suffix}"


def _endpoint_design_private_org(
    atconn,
    suffix: str = "",
):
    return f"{atconn.server}:{atconn.design_center_server_port}/org/{atconn.organization}{suffix}"


def _endpoint_auth_bearer(
    atconn,
    suffix: str = "",
):
    """Pings auth endpoint and generates a bearer token"""
    return f"{atconn.server}:{atconn.design_center_server_port}/{atconn.organization}/auth{suffix}"


def _endpoint_login_screen(
    atconn,
    suffix: str = "",
):
    """endpoint for the general login screen, get information without credentials"""
    return f"{atconn.server}:{atconn.design_center_server_port}/login{suffix}"


def _endpoint_list_projects(
    atconn,
    suffix: str = "",
):
    """gets all unpublished projects"""
    return f"{atconn.server}:{atconn.design_center_server_port}/api/1.0/org/{atconn.organization}/projects{suffix}"


def _endpoint_create_empty_project(
    atconn,
    suffix: str = "",
):
    """creates an empty project"""
    return f"{atconn.server}:{atconn.design_center_server_port}/api/1.0/org/{atconn.organization}/project/createEmpty{suffix}"
