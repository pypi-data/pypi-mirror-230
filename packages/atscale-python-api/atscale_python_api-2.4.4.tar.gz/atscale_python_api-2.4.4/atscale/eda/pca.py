import re
from atscale.db.sql_connection import SQLConnection
from atscale.data_model.data_model import DataModel
from atscale.errors.atscale_errors import EDAException, UserError
from atscale.utils import validation_utils
from atscale.utils.model_utils import _check_features
from atscale.utils.query_utils import _generate_atscale_query, generate_db_query
from typing import List, Tuple, Dict
from atscale.utils.metadata_utils import (
    _get_all_numeric_feature_names,
    _get_all_categorical_feature_names,
)
from atscale.base.enums import PlatformType, PandasTableExistsActionType
from itertools import product
import random
import string
import inspect
import logging

logger = logging.getLogger(__name__)

QR_ITERATIONS = 12


def pca(
    dbconn: SQLConnection,
    data_model: DataModel,
    pc_num: int,
    numeric_features: List[str],
    granularity_levels: List[str],
    if_exists: PandasTableExistsActionType = PandasTableExistsActionType.FAIL,
) -> Tuple[Dict, Dict]:
    """Performs principal component analysis (PCA) on the numeric features specified. This is only supported for Snowflake at this time.

    Args:
        dbconn (SQLConnection): The database connection that pca will interact with
        data_model (DataModel): The data model corresponding to the features provided
        pc_num (int): The number of principal components to be returned from the analysis. Must be in
                      the range of [1, # of numeric features to be analyzed] (inclusive)
        numeric_features (List[str]): The query names of the numeric features to be analyzed via pca
        granularity_levels (List[str]): The query names of the categorical features corresponding to the level of
                                        granularity desired in numeric_features
        if_exists (PandasTableExistsActionType, optional): The default action that pca takes when creating
                                                           a table with a preexisting name. Does not accept APPEND. Defaults to FAIL.
    Raises:
        EDAException: User must be analyzing at least two numeric features
        EDAException: Number of PCs desired must be some positive integer less than or equal to the number of numeric features
                      being analyzed
        EDAException: User may not pass constant-valued features.

    Returns:
        Tuple[DataFrame, DataFrame]: A pair of Dicts, the first containing the PCs and the second containing
                                     their percent weights
    """
    if dbconn.platform_type != PlatformType.SNOWFLAKE:
        raise UserError(f"This function is only supported for Snowflake at this time.")

    # validate the non-null inputs
    validation_utils.validate_required_params_not_none(
        local_vars=locals(),
        inspection=inspect.getfullargspec(pca),
    )

    # make sure the user inputs a valid action type
    if if_exists == PandasTableExistsActionType.APPEND:
        raise UserError(
            f"The ActionType of APPEND is not valid for this function, only REPLACE AND FAIL are valid."
        )

    dim = len(numeric_features)

    all_numeric_features = _get_all_numeric_feature_names(data_model)
    all_categorical_features = _get_all_categorical_feature_names(data_model)

    # Error checking
    ### Check that features exist in the given DataModel in the first place
    _check_features(
        numeric_features + granularity_levels,
        all_numeric_features + all_categorical_features,
    )

    ### Check that numeric/categorical features are in correct categories
    _check_features(
        numeric_features,
        all_numeric_features,
        errmsg="Make sure numeric_features consists only of numeric features",
    )
    _check_features(
        granularity_levels,
        all_categorical_features,
        errmsg="Make sure granularity_levels consists only of categorical features",
    )

    if dim < 2:
        raise EDAException(
            "Number of numeric features to be analyzed must be greater than or equal to 2"
        )

    if type(pc_num) != int or pc_num > dim or pc_num <= 0:
        raise EDAException(
            "Number of PCs must be some positive integer less than or equal to the number of features"
        )

    uuid_str = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    base_table_name = f"atscale_pca_tbl_{uuid_str}"
    logger.info(f"generating temp pca tables: {base_table_name}")

    base_table_atscale_query = generate_db_query(
        data_model=data_model,
        atscale_query=_generate_atscale_query(
            data_model=data_model, feature_list=numeric_features + granularity_levels
        ),
    )
    # Initialize base table
    base_table_query = f"CREATE TABLE {base_table_name} AS ({base_table_atscale_query}); "

    try:
        dbconn.submit_query(base_table_query)
    except Exception as e:
        err_msg = str(e)
        if "already exists." in err_msg:
            if if_exists == PandasTableExistsActionType.REPLACE:
                try:
                    dbconn.submit_query(f"DROP TABLE IF EXISTS {base_table_name}; ")
                    dbconn.submit_query(base_table_query)
                except Exception as e:
                    raise e
            else:
                table_name = re.search("Object (.*?) already exists", err_msg).group(1)
                raise UserError(
                    f"A table already exists with name: {table_name}. Name collisions between runs are rare "
                    f"but can happen. You can avoid this error by setting if_exists to REPLACE"
                )
        else:
            raise e

    # Generate queries to run PCA, display results, and drop all generated tables
    query_statements, drop_statements, display_statements = _get_pca_sql(
        base_table_name, numeric_features, pc_num, dbconn
    )

    # Check for constant-valued features
    try:
        # Run PCA off of base table
        if if_exists == PandasTableExistsActionType.REPLACE:
            dbconn.execute_statements(drop_statements)

        dbconn.execute_statements(query_statements)
    except Exception as e:
        err_msg = str(e)
        if "already exists." in err_msg:
            table_name = re.search("Object (.*?) already exists", err_msg).group(1)
            raise UserError(
                f"A table already exists with name: {table_name}. Name collisions between runs are rare "
                f"but can happen. You can avoid this error by setting if_exists to REPLACE"
            )

        # Constant-valued features will create a divide by zero error
        if "Division by zero" in err_msg:
            # Drop any tables created prior to error firing
            dbconn.execute_statements(drop_statements)
            raise EDAException("Make sure no constant-valued features are passed to pca")

    # Get results
    pc_dataframe = dbconn.submit_query(display_statements["PCs"])
    weight_dataframe = dbconn.submit_query(display_statements["Weights"])

    # Convert resulting dataframes to dictionaries
    pc_dict = {}
    weight_dict = {}

    for col in pc_dataframe:
        pc_dict[col] = pc_dataframe[col].to_numpy()

    for col in weight_dataframe:
        weight_dict[col] = weight_dataframe[col][0]

    # Drop everything written to DB
    dbconn.execute_statements(drop_statements)

    # Delete base table
    dbconn.submit_query(f"DROP TABLE {base_table_name}; ")

    # Return tuple of DFs containing 1.) PCs and 2.) their weights
    return (pc_dict, weight_dict)


def _get_pca_sql(
    table_name: str,
    table_cols: List[str],
    pc_num: int,
    dbconn: SQLConnection,
) -> Tuple:
    """Generates SQL queries that perform principal component analysis (PCA) on the data contained in the
       specified table. This implementation uses a basic QR algorithm to determine the eigenvectors and
       eigenvalues of the numeric features' covariance matrix (https://en.wikipedia.org/wiki/QR_algorithm);
       the eigenvectors are the principal components by definition, while each eigenvalue divided by the
       total of the eigenvalues represents the relative weight of the corresponding principal component.

    Args:
        table_name (str): The table containing the data to be analyzed
        table_cols (List[str]): The columns corresponding to the features to be analyzed. (Must be numeric)
        pc_num (int): The number of principal components to be returned from the analysis. Must be in
                      the range of [1, # of features to be analyzed] (inclusive)
        dbconn (SQLConnection): The database connection that pca will interact with

    Returns:
        Tuple[List[str], List[str], Dict[str:str]]: A list containing: 1.) A list of queries to initialize and
                                                    run principal component analysis, 2.) A list of queries to
                                                    delete all tables constructed by the first list, and 3.) a
                                                    dictionary containing queries to display the principal
                                                    components and their respective weights
    """
    # Make columns readable to db
    table_cols = [f"{dbconn._column_quote()}{x}{dbconn._column_quote()}" for x in table_cols]

    # Initialize lists/dict that will eventually contain all necessary queries
    query_statements = []
    drop_statements = [
        f"DROP TABLE IF EXISTS {table_name}_eigenvectors; ",
        f"DROP TABLE IF EXISTS {table_name}_v; ",
        f"DROP TABLE IF EXISTS {table_name}_r; ",
        f"DROP TABLE IF EXISTS {table_name}_q; ",
        f"DROP TABLE IF EXISTS {table_name}_covariance; ",
        f"DROP TABLE IF EXISTS {table_name}_covariance_calc; ",
        f"DROP TABLE IF EXISTS {table_name}_removed_mean; ",
        f"DROP TABLE IF EXISTS {table_name}_rowcol; ",
    ]
    display_statements = {"PCs": "", "Weights": ""}

    dim = len(table_cols)
    # The number of QR iterations to be performed; generally speaking, more iterations means tighter eigenvector/value
    # convergence and longer runtime
    iter_num = QR_ITERATIONS

    if iter_num <= 0 or type(iter_num) != int:
        raise EDAException("Number of QR iterations must be some positive integer")

    # DROP IF EXISTS string to clear tables/views in case prior run stopped short
    query_statements += drop_statements

    # Construct a table representing the data to be analyzed with the mean removed; done to center the data about the
    # origin prior to further analysis
    mean_removed_string = f"CREATE TABLE {table_name}_removed_mean AS SELECT "
    for col in table_cols:
        mean_removed_string += (
            f"{table_name}.{col} - (SELECT AVG({table_name}.{col}) "
            + f"FROM {table_name}) AS {col}, "
        )
    mean_removed_string = mean_removed_string[:-2] + f" FROM {table_name}; "

    query_statements.append(mean_removed_string)

    # Construct a table representing row/column indices; done for easy formatting of matrices in SQL
    # IDENTITY I believe is Snowflake specific
    # Can be compressed into one statement? Might not actually save time
    query_statements.append(
        f"CREATE TABLE {table_name}_rowcol (id INT IDENTITY (1, 1), r INT, c INT); "
    )

    rowcol_string = f"INSERT INTO {table_name}_rowcol (r, c) VALUES "
    for pair in product(range(1, dim + 1), range(1, dim + 1)):
        rowcol_string += f"({pair[0]}, {pair[1]}), "
    rowcol_string = rowcol_string[:-2] + "; "

    query_statements.append(rowcol_string)

    # Calculate and structure covariance matrix (https://en.wikipedia.org/wiki/Covariance_matrix); the
    # principal components and their respective weights for a set of features weights can be defined
    # in terms of the features' covariance matrix
    covariance_calc_string = f"CREATE TABLE {table_name}_covariance_calc AS "
    counter = 1
    for pair in product(table_cols, table_cols):
        covariance_calc_string += (
            f"SELECT {counter} AS id, (1. / COUNT(*)) * SUM ({pair[0]} * {pair[1]}) AS vals FROM "
            + f"{table_name}_removed_mean UNION ALL "
        )
        counter += 1
    covariance_calc_string = covariance_calc_string[:-11] + "; "

    query_statements.append(covariance_calc_string)

    covariance_string = (
        f"CREATE TABLE {table_name}_covariance AS "
        + f"SELECT {table_name}_rowcol.id, {table_name}_rowcol.r, {table_name}_rowcol.c, cf.vals FROM "
        + f"(SELECT {table_name}_covariance_calc.id AS id, vals FROM {table_name}_covariance_calc) "
        + f"AS cf JOIN {table_name}_rowcol ON {table_name}_rowcol.id = cf.id; "
    )

    query_statements.append(covariance_string)

    # Initialize Q, R, and V matrices; QR decompostion is performed below via a Gram-Schmidt variation that's modified
    # for greater numeric stability (https://www.ics.uci.edu/~xhx/courses/CS206/NLA-QR.pdf). In this process, Q is an
    # orthogonal matrix and R is an upper triangular matrix. The V matrix is initialized to the covariance matrix, and
    # its columns are iteratively updated for eventual use in calculating the columns of Q and entries of R.
    query_statements.append(
        f"CREATE TABLE {table_name}_q AS (SELECT {table_name}_covariance.id, {table_name}_covariance.r, {table_name}_covariance.c, ({table_name}_covariance.vals * 0.0) AS vals FROM {table_name}_covariance); "
    )
    query_statements.append(
        f"CREATE TABLE {table_name}_r AS (SELECT {table_name}_covariance.id, {table_name}_covariance.r, {table_name}_covariance.c, ({table_name}_covariance.vals * 0.0) AS vals FROM {table_name}_covariance); "
    )
    query_statements.append(
        f"CREATE TABLE {table_name}_v AS (SELECT * FROM {table_name}_covariance); "
    )

    for iter in range(iter_num):
        ### If not the first QR iteration, update the V matrix to reflect the values of the updated covariance matrix.
        ### Otherwise allow it to reflect the unaltered covariance matrix.
        if iter != 0:
            query_statements.append(
                f"UPDATE {table_name}_v SET r = new_v.r, c = new_v.c, vals = new_v.vals FROM "
                + f"(SELECT * FROM {table_name}_covariance) AS new_v WHERE {table_name}_v.r = new_v.r AND {table_name}_v.c = new_v.c; "
            )

        ### Update the i-th column of Q to be the normalized i-th column of V. Set R[i, i] (the i-th value along R's diagonal)
        ### to be the norm of the i-th column of V.
        for i in range(1, dim + 1):
            query_statements.append(
                f"UPDATE {table_name}_q SET vals = q{i}.vals FROM "
                + f"(SELECT r, c, vals / (SELECT SQRT(SUM(POWER(vals, 2))) FROM {table_name}_v WHERE {table_name}_v.c = {i}) AS vals FROM "
                + f"{table_name}_v WHERE {table_name}_v.c = {i}) AS q{i} WHERE {table_name}_q.c = {i} AND q{i}.c = {i} AND {table_name}_q.r = q{i}.r; "
            )
            query_statements.append(
                f"UPDATE {table_name}_r SET vals = (SELECT SQRT(SUM(POWER(vals, 2))) FROM {table_name}_v "
                + f"WHERE {table_name}_v.c = {i}) WHERE {table_name}_r.r = {i} AND {table_name}_r.c = {i}; "
            )

            ### Calculate the dot product of the i-th column of Q and the j-th column of V, set R[i, j] to this dot product,
            ### then subtract this dot product times the i-th column of Q from the j-th column of V
            for j in range(i + 1, dim + 1):
                query_statements.append(
                    f"UPDATE {table_name}_r SET vals = (SELECT SUM(q{i}.vals * v{j}.vals) FROM "
                    + f"(SELECT r, vals FROM {table_name}_q WHERE c = {i}) AS q{i} "
                    + f"JOIN (SELECT r, vals FROM {table_name}_v WHERE c = {j}) AS v{j} ON q{i}.r = v{j}.r) "
                    + f"WHERE {table_name}_r.r = {i} AND {table_name}_r.c = {j}; "
                )
                query_statements.append(
                    f"UPDATE {table_name}_v SET vals = v_minus.vals FROM "
                    + f"(SELECT v{j}.r, v{j}.c, (v{j}.vals - dot_times_q{i}.vals) AS vals FROM "
                    + f"(SELECT r, c, vals FROM {table_name}_v WHERE c = {j}) AS v{j} JOIN "
                    + f"(SELECT {table_name}_q.r, (SELECT SUM(q{i}.vals * v{j}.vals) AS vals FROM "
                    + f"(SELECT r, vals FROM {table_name}_q WHERE c = {i}) AS q{i} JOIN "
                    + f"(SELECT r, vals FROM {table_name}_v WHERE c = {j}) AS v{j} ON q{i}.r = v{j}.r) "
                    + f"* {table_name}_q.vals AS vals FROM {table_name}_q WHERE {table_name}_q.c = {i}) AS "
                    + f"dot_times_q{i} ON v{j}.r = dot_times_q{i}.r) AS v_minus WHERE "
                    + f"{table_name}_v.c = {j} AND {table_name}_v.r = v_minus.r; "
                )

        ### Update value of covariance matrix to R times Q
        covariance_update_string = f"UPDATE {table_name}_covariance SET vals = new_cov.vals FROM ("
        for col in range(1, dim + 1):
            for row in range(1, dim + 1):
                covariance_update_string += (
                    f"(SELECT {row} AS r, {col} AS c, SUM({table_name}_r_row.vals * {table_name}_q_col.vals) AS vals FROM "
                    + f"(SELECT c, vals FROM {table_name}_r WHERE r = {row} AND c > {row - 1}) AS {table_name}_r_row JOIN "
                    + f"(SELECT r, vals FROM {table_name}_q WHERE c = {col} AND r > {row - 1}) AS {table_name}_q_col ON "
                    + f"{table_name}_r_row.c = {table_name}_q_col.r) UNION ALL "
                )
        covariance_update_string = covariance_update_string[:-11]
        covariance_update_string += (
            f") AS new_cov WHERE {table_name}_covariance.r = new_cov.r AND "
            + f"{table_name}_covariance.c = new_cov.c; "
        )
        query_statements.append(covariance_update_string)

        ### Set eigenvector matrix to Q if first iteration, otherwise set value of eigenvector matrix to eigenvector
        ### matrix times Q_{i}. This is done since Q_{1} * ... * Q_{n} for n iterations converges to a matrix whose
        ### columns are the eigenvectors of the original matrix
        ### (https://stats.stackexchange.com/questions/20643/finding-matrix-eigenvectors-using-qr-decomposition).
        if iter == 0:
            query_statements.append(
                f"CREATE TABLE {table_name}_eigenvectors AS (SELECT * FROM {table_name}_q); "
            )
        else:
            eigenvector_update_string = (
                f"UPDATE {table_name}_eigenvectors SET vals = new_eig.vals FROM ("
            )
            for col in range(1, dim + 1):
                for row in range(1, dim + 1):
                    eigenvector_update_string += (
                        f"(SELECT {row} AS r, {col} AS c, SUM(old_eig_row.vals * new_q_col.vals) AS vals FROM "
                        + f"(SELECT c, vals FROM {table_name}_eigenvectors WHERE r = {row}) AS old_eig_row JOIN "
                        + f"(SELECT r, vals FROM {table_name}_q WHERE c = {col}) AS new_q_col ON "
                        + f"old_eig_row.c = new_q_col.r) UNION ALL "
                    )
            eigenvector_update_string = eigenvector_update_string[:-11]
            eigenvector_update_string += (
                f") AS new_eig WHERE {table_name}_eigenvectors.r = new_eig.r AND "
                + f"{table_name}_eigenvectors.c = new_eig.c; "
            )
            query_statements.append(eigenvector_update_string)

    # Return PCs and their weights
    ### Display PCs
    pc_display_string = "SELECT "
    for p in range(1, pc_num + 1):
        pc_display_string += f"{table_name}_eigvec{p}.vals AS pc_{p}, "
    pc_display_string = (
        pc_display_string[:-2]
        + f" FROM (SELECT r, vals FROM {table_name}_eigenvectors WHERE c = 1) AS {table_name}_eigvec1 "
    )
    for p in range(2, pc_num + 1):
        pc_display_string += f"JOIN (SELECT r, vals FROM {table_name}_eigenvectors WHERE c = {p}) AS {table_name}_eigvec{p} ON {table_name}_eigvec1.r = {table_name}_eigvec{p}.r "
    pc_display_string = pc_display_string[:-1] + "; "

    display_statements["PCs"] = pc_display_string

    ### Display relative weights
    weight_display_string = "SELECT "
    for p in range(1, pc_num + 1):
        weight_display_string += f"{table_name}_weight{p}.vals AS pc_{p}_percent_weight, "
    weight_display_string = (
        weight_display_string[:-2]
        + f" FROM (SELECT 1 AS id, vals / (SELECT SUM(vals) FROM {table_name}_r WHERE r = c) * 100 AS vals FROM {table_name}_r WHERE r = 1 AND c = 1) AS {table_name}_weight1 "
    )
    for p in range(2, pc_num + 1):
        weight_display_string += (
            f"JOIN (SELECT 1 AS id, vals / (SELECT SUM(vals) FROM {table_name}_r WHERE r = c) * 100 AS vals FROM {table_name}_r WHERE r = {p} AND c = {p}) "
            + f"AS {table_name}_weight{p} ON {table_name}_weight1.id = {table_name}_weight{p}.id "
        )
    weight_display_string = weight_display_string[:-1] + "; "

    display_statements["Weights"] = weight_display_string

    return [query_statements, drop_statements, display_statements]
