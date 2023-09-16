import base64
import logging
from typing import Dict, Optional

import pandas as pd
import yaml
from sqlalchemy import create_engine
from robot.api.deco import keyword
import matplotlib.pyplot as plt
from IPython.display import display
from robot.api import logger
from typing import List

import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly.subplots as sp

pyo.init_notebook_mode()


@keyword('Get Query from File')
def get_query_from_file(file_path: str) -> str:
    """
    Reads SQL query from file

    Args:
    | *`Name`* | *`Type`* | *`Description`* |
    | `file_path` | `(str)` | `Path to file containing SQL query.` |

    Returns:
    | *`Type`* | *`Description`* |
    | `(str)` | `SQL query as a string.` |
    """
    logger.info('Step 1: Reading SQL query from file...')
    with open(file_path, 'r') as file:
        return file.read()


def execute_query(query: str, config_file_path: str, database_config_name: str,
                  query_params: Optional[Dict] = None) -> pd.DataFrame:
    """
    Executes an SQL query on a specified database configuration using SQLAlchemy.

    Args:
    | *`Name`* | *`Type`* | *`Description`* |
    | `query` | `(str)` | `SQL query to execute.` |
    | `config_file_path` | `(str)` | `Path to the configuration file containing the database configurations.` |
    | `database_config_name` | `(str)` | `Name of the database configuration in the config file.` |
    | `query_params` | `(Optional[Dict])` | `Optional dictionary of query parameters.` |

    Returns:
    | *`Type`* | *`Description`* |
    | `pandas.DataFrame` | `A Pandas DataFrame containing the results of the SQL query.` |

    Configuration file structure:
    ```
    database_configurations:
        my_database:
            username: my_username
            password: my_password
            host: my_host
            port: my_port
            service_name: my_service_name
    ```

    Examples:
    | *`Robot Framework`* |                                                                                   |
    | `Execute Query`     | `query=SELECT * FROM my_table` `config_file_path=/path/to/config.yaml` `database_config_name=my_database` |
    |                      | `query_params={"param1": "value1"}`                                        |
    """
    # Step 1: Load database configuration from config file
    logging.info('Step 1: Loading database configuration from config file...')
    with open(config_file_path, 'r') as file:
        config = yaml.safe_load(file)
    db_config = config['database_configurations'][database_config_name]

    # Step 2: Connect to database using SQLAlchemy
    logging.info('Step 2: Connecting to database using SQLAlchemy...')
    password = base64.b64decode(db_config['password'].encode()).decode()  # decode base64-encoded password
    engine = create_engine(
        f"oracle://{db_config['username']}:{password}@{db_config['host']}:{db_config['port']}/?service_name={db_config['service_name']}")

    # Step 3: Execute SQL query
    logging.info('Step 3: Executing SQL query...')
    if query_params:
        result = pd.read_sql_query(query, engine, params=query_params)
    else:
        result = pd.read_sql_query(query, engine)

    result = result.fillna('')

    return result


@keyword('Visualize Data')
def visualize_data(dataframe: pd.DataFrame, x_col: str, y_col: str, plot_type: str = 'bar',
                   title: str = 'Data Visualization', plot_name: str = 'Trace') -> None:
    """
    Visualizes query results as a plot and displays them as a DataFrame.

    Args:
    | *`Name`* | *`Type`* | *`Description`* |
    | *`dataframe`* | `pandas.DataFrame` | A Pandas DataFrame containing the results of the SQL query. |
    | *`x_col`*     | `str`             | The name of the column to use for the x-axis of the plot. |
    | *`y_col`*     | `str`             | The name of the column to use for the y-axis of the plot. |
    | *`plot_type`*  | `str`             | The type of plot to use. Default is 'bar', but can be 'line', 'scatter', etc. |
    | *`title`*      | `str`             | The title of the plot. Default is 'Data Visualization'. |
    | *`plot_name`*  | `str`             | The name of the trace in the plot. Default is 'Trace'. |

    Examples:
    | *Keyword*              | *Arguments*                                                               |
    | `Visualize Data`       | dataframe=x, x_col=column_name_1, y_col=column_name_2, plot_type='bar', title='Bar Plot', plot_name='Trace' |
    | `Visualize Data`       | dataframe=y, x_col=column_name_3, y_col=column_name_4, plot_type='scatter', title='Scatter Plot', plot_name='Data' |
    | `Visualize Data`       | dataframe=z, x_col=column_name_5, y_col=column_name_6, plot_type='line', title='Line Plot', plot_name='Line Data' |
    """

    # Step 1: Visualize data as plot
    logger.info(f"Step 1: Visualizing data as {plot_type} plot...")

    trace = go.Bar(x=dataframe[x_col], y=dataframe[y_col], name=plot_name)

    data = [trace]
    layout = go.Layout(title=title, barmode='group', height=600, showlegend=True,
                       margin=dict(l=50, r=50, t=50, b=50))
    fig = go.Figure(data=trace, layout=layout)
    fig.update_layout(xaxis_title=x_col.replace('_', ' ').capitalize(),
                      yaxis_title=y_col.replace('_', ' ').capitalize())

    pyo.iplot(fig)

    # Step 2: Create and display the table
    logger.info("Step 2: Displaying data as a DataFrame table...")

    table = ff.create_table(dataframe)
    table.layout.autosize = False
    table.layout.width = 800
    table.layout.align = 'center'  # Set the alignment to center

    pyo.iplot(table)

    # Old code
    # Step 1: Visualize data as plot
    # logger.info(f"Step 1: Visualizing data as {plot_type} plot...")
    # plt.figure(figsize=(15, 5))
    #
    # if plot_type == 'bar':
    #     plt.bar(dataframe[x_col], dataframe[y_col])
    # elif plot_type == 'line':
    #     plt.plot(dataframe[x_col], dataframe[y_col])
    # elif plot_type == 'scatter':
    #     plt.scatter(dataframe[x_col], dataframe[y_col])
    # else:
    #     raise ValueError(f"Invalid plot type '{plot_type}'. Supported types are 'bar', 'line', 'scatter'.")
    #
    # plt.xlabel(x_col)
    # plt.ylabel(y_col)
    # plt.title('Query Results')
    # plt.show()
    #
    # # Step 2: Display data as DataFrame
    # logger.info('Step 2: Displaying data as DataFrame...')
    # display(dataframe)


@keyword('Execute SQL Query and Visualize Data')
def execute_sql_query_and_visualize_data(query_file_path: str, config_file_path: str, database_config_name: str,
                                         x_col: str, y_col: str, chart_type: str = 'bar') -> None:
    """
    Executes an SQL query and visualizes the results as a chart.

    Args:
    | *`Name`* | *`Type`* | *`Description`* |
    | *`query_file_path`*     | `str` | Path to the file containing the SQL query to execute.     |
    | *`config_file_path`*    | `str` | Path to the configuration file containing the database configurations. |
    | *`database_config_name`*| `str` | Name of the database configuration in the config file.  |
    | *`x_col`*               | `str` | The name of the column to use for the x-axis of the chart. |
    | *`y_col`*               | `str` | The name of the column to use for the y-axis of the chart. |
    | *`chart_type`*          | `str` | The type of chart to use. Can be one of "bar", "line", "scatter", "histogram". Default is "bar". |

    Examples:
    | *Keyword*                              | *Arguments*                                                       |
    | `Execute SQL Query and Visualize Data` | query_file_path=/path/to/query.sql, config_file_path=/path/to/config.yaml, database_config_name=my_database, x_col=column_name_1, y_col=column_name_2, chart_type=bar |
    """
    # Step 1: Get SQL query from file
    logger.info('Step 1: Get SQL query from file...')
    query = get_query_from_file(query_file_path)

    # Step 2: Execute SQL query
    logger.info('Step 2: Execute SQL query...')
    result = execute_query(query, config_file_path, database_config_name)

    # Step 3: Visualize data
    logger.info('Step 3: Visualizing data...')
    if chart_type == 'bar':
        visualize_data.bar_chart(result, x_col, y_col)
    elif chart_type == 'line':
        visualize_data.line_chart(result, x_col, y_col)
    elif chart_type == 'scatter':
        visualize_data.scatter_plot(result, x_col, y_col)
    elif chart_type == 'histogram':
        visualize_data.histogram(result, x_col, y_col)
    else:
        raise ValueError(
            f'Invalid chart type: {chart_type}. Supported chart types are: "bar", "line", "scatter", "histogram"')


@keyword('Get DataFrame Columns')
def get_dataframe_columns(dataframe: pd.DataFrame) -> List[str]:
    """
    Returns the column names of a Pandas DataFrame.

    Args:
    | *`Name`* | *`Type`* | *`Description`* |
    | *`dataframe`* | `pandas.DataFrame` | A Pandas DataFrame to get column names from. |

    Returns:
    A list of column names.

    Examples:
    | *Keyword*              | *Arguments*                            |
    | `Get DataFrame Columns`| dataframe=my_dataframe                 |
    """
    # Step 1: Get dataframe columns
    logger.info('Step 1: Getting dataframe columns...')
    return dataframe.columns.tolist()

# *** Settings ***
# Library  MyLibrary.py
#
# *** Variables ***
# ${QUERY_FILE_PATH}  /path/to/query.sql
# ${CONFIG_FILE_PATH}  /path/to/config.yaml
# ${DATABASE_CONFIG_NAME}  my_database
# ${X_COL}  column1
# ${Y_COL}  column2
# ${PLOT_TYPE}  bar
#
# *** Tasks ***
# Get Query from File
#     [Documentation]  Retrieves a query from a SQL file
#     [Task]  ${query}=  Get Query from File  file_path=${QUERY_FILE_PATH}
#     [Return]  ${query}
#
# Execute Query
#     [Documentation]  Executes a SQL query using a database configuration
#     [Task]  ${query}=  Get Query from File  file_path=${QUERY_FILE_PATH}
#     ...  config_file_path=${CONFIG_FILE_PATH}
#     ...  database_config_name=${DATABASE_CONFIG_NAME}
#     ${results}=  Execute Query  query=${query}  config_file_path=${CONFIG_FILE_PATH}  database_config_name=${DATABASE_CONFIG_NAME}
#     [Return]  ${results}
#
# Visualize Data
#     [Documentation]  Generates a visualization of data using a given plot type
#     [Task]  ${query}=  Get Query from File  file_path=${QUERY_FILE_PATH}
#     ...  config_file_path=${CONFIG_FILE_PATH}
#     ...  database_config_name=${DATABASE_CONFIG_NAME}
#     ${results}=  Execute Query  query=${query}  config_file_path=${CONFIG_FILE_PATH}  database_config_name=${DATABASE_CONFIG_NAME}
#     Visualize Data  dataframe=${results}  x_col=${X_COL}  y_col=${Y_COL}  plot_type=${PLOT_TYPE}
#
# Execute Query and Visualize Data
#     [Documentation]  Executes a SQL query using a database configuration and generates a visualization of data
#     [Task]  ${query}=  Get Query from File  file_path=${QUERY_FILE_PATH}
#     ...  config_file_path=${CONFIG_FILE_PATH}
#     ...  database_config_name=${DATABASE_CONFIG_NAME}
#     ${results}=  Execute Query  query=${query}  config_file_path=${CONFIG_FILE_PATH}  database_config_name=${DATABASE_CONFIG_NAME}
#     Visualize Data  dataframe=${results}  x_col=${X_COL}  y_col=${Y_COL}  plot_type=${PLOT_TYPE}
