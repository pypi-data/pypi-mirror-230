import pandas as pd
from sklearn.datasets import make_blobs
import numpy as np
import teradataml as tdml
import os

import functools


def upload_to_vantage(default_table_name='anomaly_dataset', default_types = None):
    def decorator(f):
        @functools.wraps(f)
        def wrapped_f(*args, **kwargs):

            # Call the function to generate the pandas dataframe
            df = f(*args, **kwargs)

            # Extract table_name from kwargs, use default_table_name if not provided
            table_name = kwargs.get('table_name', default_table_name)
            types      = kwargs.get('types', default_types)

            # Upload the dataset in Vantage
            tdml.copy_to_sql(df, table_name=table_name, types=types, **kwargs)
            if 'schema_name' in kwargs.keys():
                print('Dataset uploaded in ' + kwargs['schema_name'] + '.' + table_name)
            else:
                print('Schema_name not specified. Default used.')
                print('Dataset uploaded in ' + table_name)

            if 'schema_name' in kwargs.keys():
                df = tdml.DataFrame(tdml.in_schema(kwargs['schema_name'], table_name))
            else:
                df = tdml.DataFrame(table_name)

            return df

        return wrapped_f
    return decorator

train_dataset_filename = 'train_dataset.csv'
package_dir, _ = os.path.split(__file__)

@upload_to_vantage(default_table_name='train_dataset', default_types={"events": tdml.VARCHAR(length = 1000, charset = 'LATIN')})
def event_dataset(**kwargs):
    return train_dataset()
@upload_to_vantage(default_table_name='anomaly_dataset')
def anomaly_dataset(n_samples=10000, n_features=6, anomaly_pct=0.05,**kwargs):
    """
    This function generates a pandas DataFrame that simulates a dataset with both normal and anomalous data.

    Parameters:
    n_samples (int): The total number of samples (rows) in the dataset. Default is 10000.
    n_features (int): The number of features (columns) in the dataset. Default is 6.
    anomaly_pct (float): The proportion of anomalies in the dataset. Default is 0.05.

    Returns:
    df (DataFrame): A pandas DataFrame with the generated data. It includes 'id', features, and 'anomaly' columns.
                    The 'anomaly' column indicates if the row is an anomaly (1) or not (0).
    """

    # Generate the data for the dataframe
    data = np.random.randn(n_samples, n_features)

    # Add anomalies to the data
    num_anomalies = int(anomaly_pct * n_samples)
    anomaly_idx = np.random.choice(n_samples, num_anomalies, replace=False)
    data[anomaly_idx] = np.random.uniform(low=-10, high=10, size=(num_anomalies, n_features))

    # Create a pandas dataframe from the data
    df = pd.DataFrame(data, columns=[f'feature_{i}' for i in range(1, n_features + 1)])
    df['id'] = df.index
    df = df[['id'] + [f'feature_{i}' for i in range(1, n_features + 1)]]
    df['anomaly'] = 0
    df.iloc[list(anomaly_idx), -1] = 1

    return df


@upload_to_vantage(default_table_name='cluster_dataset')
def cluster_dataset(n_samples=10000, centers=3, n_features=6, cluster_std=3, random_state=42,**kwargs):
    """
    This function generates a pandas DataFrame that simulates a dataset with distinct clusters.

    Parameters:
    n_samples (int): The total number of samples (rows) in the dataset. Default is 10000.
    centers (int): The number of clusters in the dataset. Default is 3.
    n_features (int): The number of features (columns) in the dataset. Default is 6.
    cluster_std (int): The standard deviation of clusters. Default is 3.
    random_state (int): A seed used by the random number generator to maintain the reproducibility of dataset. Default is 42.

    Returns:
    df (DataFrame): A pandas DataFrame with the generated data. It includes 'id' and feature columns.
                    Each row represents a point in the n-dimensional feature space.
    """

    # Generate synthetic dataset with specified clusters and features
    X, y = make_blobs(n_samples=n_samples, centers=centers, n_features=n_features, random_state=random_state,
                      cluster_std=cluster_std)

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(1, n_features + 1)])
    df['id'] = df.index
    df = df[['id'] + [f'feature_{i}' for i in range(1, n_features + 1)]]

    return df


def train_dataset():
    return pd.read_csv(os.path.join(package_dir, "data", train_dataset_filename),parse_dates =  ['datetime'])

def upload_train_dataset(table_name='train_dataset', **kwargs):
    if 'schema_name' in kwargs.keys():
        print('dataset uploaded in '+ kwargs['schema_name'] + '.' + table_name)
    else:
        print('schema_name not specified. default used')
        print('dataset uploaded in '+table_name)

    tdml.copy_to_sql(df=train_dataset(),
                     table_name=table_name,
                     types = {"events": tdml.VARCHAR(length = 1000, charset = 'LATIN')},
                     **kwargs)

    if 'schema_name' in kwargs.keys():
        df = tdml.DataFrame(tdml.in_schema(kwargs['schema_name'], table_name))
    else:
        df = tdml.DataFrame(table_name)

    return df

