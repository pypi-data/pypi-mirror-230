from tqdm import tqdm
import teradataml as tdml
from teradataml import valib
import matplotlib.pyplot as plt
def compute_cluster_inertia(kmeans_model, kmeans_out, features):
    """
    Compute the inertia and distortion of the clusters for a k-means clustering model.

    Parameters:
    - kmeans_model: The k-means model containing the results (assumed to have a "result._table_name" attribute).
    - kmeans_out: The output of the k-means model (assumed to have a "result._table_name" attribute).
    - features: List of feature names used in the clustering.

    Returns:
    - Tuple containing (inertia, distortion) values.

    Notes:
    - Inertia is the sum of squared distances of samples to their closest cluster center.
    - Distortion is the average of the squared distances.
    """

    # Construct the sum of squared distances operation for each feature.
    operation = '+'.join(['(A.' + x + '-B.' + x + ')**2' for x in features])

    # Prefix feature names with 'A.' for the kmeans_model table.
    A = ['A.' + x for x in features]

    # Prefix feature names with 'B.' for the kmeans_out table.
    B = ['B.' + x for x in features]

    # Construct a subquery to calculate sum of squared distances for each cluster.
    subquery = f"""
        SEL 
            A.clusterid
        ,   SUM({operation}) AS sum_sq_distance
        FROM {kmeans_model.result._table_name} A
        INNER JOIN {kmeans_out.result._table_name} B
        ON A.clusterid = B.clusterid
        GROUP BY 1
    """

    # Construct the main query to compute inertia (sum) and distortion (average) of the squared distances.
    query = f"""
    SEL SUM(B.sum_sq_distance) as inertia, AVG(B.sum_sq_distance) as distorsion
    FROM (
        {subquery}
    ) B
    """

    # Execute the SQL query and convert the result into a pandas dataframe.
    df = tdml.DataFrame.from_query(query).to_pandas()

    # Extract the inertia and distortion values and return them.
    return df.inertia.values[0], df.distorsion.values[0]


def get_kmeanspredict(schema_name):
    """
    Retrieve a list of k-means prediction tables from a specified database schema.

    Parameters:
    - schema_name (str): The name of the database schema to search in.

    Returns:
    - List of table names that are k-means prediction tables.

    Notes:
    - This function looks for tables that either start with 'ml__valib_kmeanspredict_'
      or 'ml__td_sqlmr_volatile_out' to identify them as k-means prediction tables.
    """

    # Fetch all table names in the provided schema.
    all_tables = tdml.db_list_tables(schema_name=schema_name).TableName.values

    # Filter the tables based on their naming convention to identify k-means prediction tables.
    kmeans_tables = [
        x for x in all_tables
        if x.startswith('ml__valib_kmeanspredict_') or x.startswith('ml__td_sqlmr_volatile_out')
    ]

    return kmeans_tables


def cleanup_kmeanspredict(schema_name, table_names=None):
    """
    Clean up (delete) k-means prediction tables from a specified database schema.

    Parameters:
    - schema_name (str): The name of the database schema to clean up.
    - table_names (list, optional): List of table names to delete. If not provided,
      the function fetches the list of k-means prediction tables using get_kmeanspredict().

    Returns:
    - None

    Notes:
    - This function deletes tables either provided in table_names or those identified
      by the get_kmeanspredict() function.
    - Deletion failures are silently ignored.
    """

    # If no table names are provided, fetch the list of k-means prediction tables.
    if table_names is None:
        table_names = get_kmeanspredict(schema_name)

    # Iterate over each table and attempt to delete it.
    for t in table_names:
        try:
            tdml.db_drop_table(table_name=t, schema_name=schema_name)
        except:
            # If an error occurs during table deletion, ignore and move on.
            continue
