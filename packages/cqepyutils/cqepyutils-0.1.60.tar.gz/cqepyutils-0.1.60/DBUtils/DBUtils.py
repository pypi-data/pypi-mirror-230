import logging
import pandas as pd
from sqlalchemy import create_engine
import base64
import yaml
import matplotlib.pyplot as plt
from IPython.display import display


def get_query_from_file(file_path):
    """
    Reads SQL query from file

    :param file_path: path to file containing SQL query
    :return: SQL query as a string
    """
    logging.info('Step 1: Reading SQL query from file...')
    with open(file_path, 'r') as file:
        return file.read()


def execute_query(query, database_config_name, query_params=None):
    """
    Executes SQL query on specified database configuration using SQLAlchemy

    :param query: SQL query to execute
    :param database_config_name: name of database configuration in config file
    :param query_params: optional dictionary of query parameters
    :return: pandas dataframe containing query results
    """
    # Step 1: Load database configuration from config file
    logging.info('Step 1: Loading database configuration from config file...')
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    db_config = config['database_configurations'][database_config_name]

    # Step 2: Connect to database using SQLAlchemy
    logging.info('Step 2: Connecting to database using SQLAlchemy...')
    password = base64.b64decode(db_config['password'].encode()).decode()  # decode base64-encoded password
    engine = create_engine(
        f"oracle://{db_config['username']}:{password}@{db_config['host']}:{db_config['port']}/{db_config['service_name']}")

    # Step 3: Execute SQL query
    logging.info('Step 3: Executing SQL query...')
    if query_params:
        result = pd.read_sql_query(query, engine, params=query_params)
    else:
        result = pd.read_sql_query(query, engine)

    return result


def plot_data(dataframe):
    """
    Plots query results as a graph and displays them as a dataframe

    :param dataframe: pandas dataframe containing query results
    """
    # Step 1: Plot data as graph
    logging.info('Step 1: Plotting data as graph...')
    plt.figure(figsize=(15, 5))
    plt.plot(dataframe.iloc[:, 0], dataframe.iloc[:, 1], label='Data')
    plt.xlabel(dataframe.columns[0])
    plt.ylabel(dataframe.columns[1])
    plt.title('Query Results')
    plt.legend()
    plt.show()

    # Step 2: Display data as DataFrame
    logging.info('Step 2: Displaying data as DataFrame...')
    display(dataframe)


# if __name__ == '__main__':
#     # Configure logger
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
#
#     # Step 1: Read SQL query from file
#     logging.info('Step 1: Reading SQL query from file...')
#     query = get_query_from_file('query.sql')
#
#     # Step 2: Execute SQL query
#     logging.info('Step 2: SQL query read successfully!')
#     database_config_name = 'dev'
#     result = execute_query(query, database_config_name)
#
#     # Step 3: Plot query results
#     logging.info('Step 3: Plotting query results...')
#     plot_data(result)
