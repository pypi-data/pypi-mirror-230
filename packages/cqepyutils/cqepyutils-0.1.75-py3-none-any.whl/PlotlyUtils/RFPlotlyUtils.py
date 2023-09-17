import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from robot.api.deco import keyword
from robot.api import logger


@keyword('Visualize Data')
def visualize_data(*dataframes, x_col: str, y_col: str,
                   plot_type: str = 'bar', titles: list = None, plot_name: str = 'Trace') -> None:
    """
    Visualizes query results as a plot and displays them as a DataFrame.

    Args:
        *dataframes (pd.DataFrame): Variable number of Pandas DataFrames.
        x_col (str): The name of the column to use for the x-axis of the plot.
        y_col (str): The name of the column to use for the y-axis of the plot.
        plot_type (str, optional): The type of plot to use. Default is 'bar', but can be 'line', 'scatter', etc.
        titles (list, optional): A list of titles for each table. Default is None.
        plot_name (str, optional): The name of the trace in the plot. Default is 'Trace'.

    Examples:
        | *Keyword*          | *Arguments*                                                               |
        | `Visualize Data`   | dataframe=x, dataframe2=y, x_col=column_name_1, y_col=column_name_2, plot_type='bar', titles=['Table 1', 'Table 2'], plot_name='Trace' |
        | `Visualize Data`   | dataframe=x, dataframe2=y, x_col=column_name_3, y_col=column_name_4, plot_type='scatter', titles=['Table A', 'Table B'], plot_name='Data' |
        | `Visualize Data`   | dataframe=x, dataframe2=y, x_col=column_name_5, y_col=column_name_6, plot_type='line', titles=['Table X', 'Table Y'], plot_name='Line Data' |
    """

    num_dataframes = len(dataframes)

    if titles is None or len(titles) != num_dataframes:
        titles = ['Table {}'.format(i + 1) for i in range(num_dataframes)]

    logger.info(f'Step - 1: Starting data visualization for {num_dataframes} dataframes.')

    if num_dataframes == 1:
        # If only one dataframe is provided, display it in the center
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(dataframes[0].columns),
                        fill_color='rgb(0, 102, 204)',  # Header background color (blue)
                        font=dict(color='white')),  # Header font color
            cells=dict(values=dataframes[0].to_numpy().T.tolist(),
                       fill_color=[[['#f9f9f9', '#ffffff'][i % 2] for i in range(len(dataframes[0]))]],  # Alternating row colors
                       font=dict(color='black'))  # Rows font color
        )])
        fig.update_layout(title=titles[0])
    else:
        # If multiple dataframes are provided, create subplots in a grid layout
        num_rows = (num_dataframes + 1) // 2
        fig = make_subplots(rows=num_rows, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]] * num_rows)

        for i, (dataframe, title) in enumerate(zip(dataframes, titles)):
            row = (i // 2) + 1
            col = (i % 2) + 1

            table = go.Table(
                header=dict(values=list(dataframe.columns),
                            fill_color='rgb(0, 102, 204)',  # Header background color (blue)
                            font=dict(color='white')),  # Header font color
                cells=dict(values=dataframe.to_numpy().T.tolist(),
                           fill_color=[[['#f9f9f9', '#ffffff'][i % 2] for i in range(len(dataframe))]],  # Alternating row colors
                           font=dict(color='black'))  # Rows font color
            )

            fig.add_trace(table, row=row, col=col)
            fig.update_layout(title=title)

    # Update layout
    fig.update_layout(
        height=500 * ((num_dataframes + 1) // 2) if num_dataframes > 1 else 500,  # Adjust height based on the number of rows
        margin=dict(t=50, l=50, r=50),
    )

    logger.info(f'Step - 2: Data visualization complete for {num_dataframes} dataframes.')


@keyword('Visualize Data1')
def visualize_data1(*dataframes, titles: list = None) -> None:
    """
    Visualizes query results as a plot and displays them as a DataFrame.

    Args:
        *dataframes (pd.DataFrame): Variable number of Pandas DataFrames.
        titles (list, optional): A list of titles for each table. Default is None.

    Examples:
        | *Keyword*          | *Arguments*                                                               |
        | `Visualize Data`   | dataframe=x, titles=['Table 1']                                           |
        | `Visualize Data`   | dataframe=y, titles=['Table 2']                                           |
    """

    num_dataframes = len(dataframes)

    if titles is None or len(titles) != num_dataframes:
        titles = ['Table {}'.format(i + 1) for i in range(num_dataframes)]

    logger.info(f'Step - 1: Starting data visualization for {num_dataframes} dataframes.')

    fig = make_subplots(rows=1, cols=num_dataframes)

    for i, (df, title) in enumerate(zip(dataframes, titles)):
        table = ff.create_table(df)
        for trace in table.data:
            fig.add_trace(trace)

        fig.update_layout(title=title)

    # Update layout
    fig.update_layout(
        height=500,
        margin=dict(t=50, l=50, r=50),
    )

    fig.show()

    logger.info(f'Step - 2: Data visualization complete for {num_dataframes} dataframes.')
