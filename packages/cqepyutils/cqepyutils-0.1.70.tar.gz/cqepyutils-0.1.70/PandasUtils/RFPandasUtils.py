import os
import filecmp
import difflib
import csv
from typing import List, Tuple
from typing import Union
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from robot.api import logger
from robot.api.deco import keyword
from DBUtils import RFDBUtils


@keyword('Find Delimiter In File')
def find_delimiter(filename: str) -> Union[str, None]:
    """
    Find the delimiter used in a CSV file.

    `Args:`
    | *`Name`* | *`Type`* | *`Description`* |
    | `filename`|  The name of the CSV file.

    `Returns:`
    | *`Type`* | *`Description`* |
    | `str` | `The delimiter used in the CSV file as a string.` |

    Examples:
    | ${delimiter} | Find Delimiter | example.csv |
    """
    _, ext = os.path.splitext(filename)

    if ext in ['.xls', '.xlsx']:
        logger.info(f'{filename} is an Excel file. Cannot find delimiter.')
        return None

    try:
        with open(filename, 'rb') as f:
            # Read a sample of the data to analyze the dialect
            sample = f.read(1024).decode()

            # List of delimiters to test
            delimiters = [',', '\t', ';', '|', ':', '~', '\x01']
            delimiter_str = "".join(delimiters)

            # Use csv.Sniffer to guess the dialect
            dialect = csv.Sniffer().sniff(sample, delimiters=delimiter_str)

        delimiter = chr(getattr(dialect, 'delimiter'))

        # Log the delimiter
        logger.info(f'The delimiter in {filename} is "{delimiter}"')

        return delimiter
    except UnicodeDecodeError:
        logger.info(f'{filename} is not a delimiter file')
        return None


@keyword(name="Create Dataframe From File")
def create_dataframe_from_file(file_path: str, delimiter: str = None, has_header: bool = True,
                               width: list = None, colspecs: list = None,
                               column_names: list = None, dtypes: dict = None,
                               encoding: str = 'ISO-8859-1',
                               on_bad_lines: str = 'warn', skiprows: int = 0, skipfooter: int = 0):
    """
    Creates a Pandas DataFrame from a CSV, PSV, or fixed-width file.

    `Args:`
    | *`Name`* | *`Type`* | *`Description`* |
    | `file_path`    | `(str)` | `The path to the input file.` |
    | `delimiter`    | `(str)` | The delimiter character used in the input file. Default is ','.` |
    | `has_header`   | `(bool)` | `Whether the input file has headers. Default is True.` |
    | `width`        | `(list or tuple)` | `A list or tuple of integers specifying the width of each fixed-width field. Required when reading a fixed-width file. Default is None.` |
    | `encoding`     | `(str)` | `The encoding of the input file. Default is 'ISO-8859-1'.` |
    | `on_bad_lines` | `(str)` | `What to do with bad lines encountered in the input file. Valid values are 'raise', 'warn', and 'skip'. Default is 'warn'.` |
    | `skiprows`     | `(int or list-like)` | `Line numbers to skip (0-indexed) or number of lines to skip (int) at the start of the file. Default is 0.` |
    | `skipfooter`   | `(int)` | `Number of lines to skip at the end of the file. Default is 0.` |

    `Returns:`
    | *`Type`* | *`Description`* |
    | `pandas.DataFrame` | `The DataFrame created from the input file.` |

    Examples:
    | Create Dataframe From File | /path/to/file.csv |
    | Create Dataframe From File | /path/to/file.psv | delimiter='|', has_header=False |
    | Create Dataframe From File | /path/to/file.xlsx | has_header=False |
    | Create Dataframe From File | /path/to/file.fwf | width=[10, 20, 30] |
    | Create Dataframe From File | /path/to/file.csv | encoding='utf-8', on_bad_lines='raise' |
    """

    # Set default dtypes as 'str' if not provided
    if dtypes is None:
        dtypes = 'str'

    # Determine if the file has a delimiter based on the provided delimiter
    has_delimiter = delimiter is not None and delimiter != ''

    # Determine the file type based on the file extension
    file_ext = file_path.split('.')[-1].lower()
    if has_delimiter:
        # Log info message
        logger.info(f"        Reading delimited file '{file_path}' with delimiter '{delimiter}' and encoding '{encoding}'")
        # Read delimited file into a DataFrame
        df = pd.read_csv(file_path, delimiter=delimiter, header=None if not has_header else 'infer',
                         names=column_names, encoding=encoding, on_bad_lines=on_bad_lines,
                         skiprows=skiprows, skipfooter=skipfooter, dtype=dtypes, index_col=False, engine='python')
    elif file_ext == 'xlsx':
        # Log info message
        logger.info(f"        Reading Excel file '{file_path}'")
        # Read Excel file into a DataFrame
        df = pd.read_excel(file_path, skiprows=skiprows, skipfooter=skipfooter, dtype=dtypes)
    elif file_ext == 'dat':
        if width is not None:
            # Log info message
            logger.info(f"        Reading fixed-width file '{file_path}' with specified width")
            # Read fixed-width file into a DataFrame using width parameter
            df = pd.read_fwf(file_path, widths=width, header=None if not has_header else 'infer', names=column_names,
                             encoding=encoding, on_bad_lines=on_bad_lines,
                             skiprows=skiprows, skipfooter=skipfooter, dtype=dtypes, index_col=False)
        elif colspecs is not None:
            # Log info message
            logger.info(f"        Reading fixed-width file '{file_path}' with specified colspecs")
            # Read fixed-width file into a DataFrame using colspecs parameter
            df = pd.read_fwf(file_path, colspecs=colspecs, header=None if not has_header else 'infer',
                             names=column_names, encoding=encoding, on_bad_lines=on_bad_lines,
                             skiprows=skiprows, skipfooter=skipfooter, dtype=dtypes, index_col=False)
        else:
            # Log error message and raise exception
            logger.error("Error: For '.dat' files, you must provide either 'width' or 'colspecs'.")
            raise Exception("Invalid '.dat' file configuration")
    else:
        # Log error message and raise exception
        logger.error(f"Error: Unsupported file type '{file_ext}'. "
                     f"Supported file types are 'csv', 'psv', 'xlsx', and 'dat'.")
        raise Exception(f"Unsupported file type '{file_ext}'")

    # Log info message
    logger.info(f"        DataFrame created with {df.shape[0]} rows and {df.shape[1]} columns")
    # Return the DataFrame
    return df


@keyword("Write DataFrame To CSV File")
def write_df_to_csv(df_to_write: pd.DataFrame, file_path: str, file_name: str, index: bool = False):
    """
    Write the DataFrame to a CSV file.

    `Args:`
    | *`Name`* | *`Type`* | *`Description`* |
    | `df_to_write`    | `pandas.DataFrame` | `The DataFrame to write to the CSV file.` |
    | `file_path`    | `str` | `The path where the CSV file needs to be created.` |
    | `file_name`    | `str` | `The name of the CSV file to be created.` |
    | `index`    | `bool` | `Whether to include the index in the CSV file. Default is False.` |

    `Returns:`
    | *`Type`* | *`Description`* |
    | `None`    | `This method does not return anything.` |

    Examples:
    | Write DataFrame To CSV File | ${df} | /path/to/file/ | example.csv |
    | Write DataFrame To CSV File | ${df} | /path/to/file/ | example.csv | True |
    """
    logger.info('Step 1: Writing DataFrame to CSV file...')
    try:
        df_to_write.to_csv(path_or_buf=file_path + '/' + file_name, mode='w', index=index)
        logger.info('Step 2: Writing DataFrame to CSV file completed successfully.')
    except Exception as e:
        logger.error(f'Step 2: Writing DataFrame to CSV file failed with error: {e}')


@keyword("Write DataFrame To PSV File")
def write_df_to_psv(df_to_write: pd.DataFrame, file_path: str, file_name: str):
    """
    Write the DataFrame to a PSV (pipe-separated values) file.

    `Args:`
    | *`Name`* | *`Type`* | *`Description`* |
    | `df_to_write` | `pandas.DataFrame` | `The DataFrame to write to the PSV file.` |
    | `file_path` | `str` | `The path where the PSV file needs to be created.` |
    | `file_name` | `str` | `The name of the PSV file to be created.` |

    `Returns:`
    | *`Type`* | *`Description`* |
    | `None` | `This method does not return anything.` |

    Examples:
    | Write DataFrame To PSV File | ${df} | /path/to/file/ | example.psv |
    """

    logger.info('Step 1: Writing DataFrame to PSV file...')
    try:
        df_to_write.to_csv(path_or_buf=file_path + '/' + file_name, mode='w', sep='|', index=False)
        logger.info('Step 2: Writing DataFrame to PSV file completed successfully.')
    except Exception as e:
        logger.error(f'Step 2: Writing DataFrame to PSV file failed with error: {e}')


@keyword("Compare All File Contents In Directories")
def df_diff(source_file_path_name: str, target_file_path_name: str, delimiter: str = None, has_header: bool = True,
            width: list = None, colspecs: list = None, column_names: list = None, dtypes: dict = None,
            encoding: str = 'ISO-8859-1', on_bad_lines: str = 'warn', skiprows: int = 0, skipfooter: int = 0,
            key_columns: list = None, ignore_columns: list = None, report_type: str = 'all'):
    """
    Compare the difference between two files' contents and generate a detailed mismatch report.

    `Args:`
    | *`Name`* | *`Type`* | *`Description`* |
    | `source_file_path_name` | `(str)` | `The path to the first file containing the source DataFrame to compare.` |
    | `target_file_path_name` | `(str)`  | `The path to the second file containing the target DataFrame to compare.` |
    | `delimiter` | `(str)` | `The delimiter character used in the input files. Default is ','.` |
    | `has_header` | `(bool)` | `Whether the input files have headers. Default is True.` |
    | `width` | `(list or tuple)` | `A list or tuple of integers specifying the width of each fixed-width field. Required when reading a fixed-width file. Default is None.` |
    | `colspecs` | `(list or tuple)` | `A list or tuple of pairs (int, int) specifying the column ranges for fixed-width fields. Required when reading a fixed-width file. Default is None.` |
    | `column_names` | `(list)` | `A list of column names to use if the input files do not have headers.` |
    | `dtypes` | `(dict)` | `A dictionary specifying the data types of columns in the DataFrame.` |
    | `encoding` | `(str)` | `The encoding of the input files. Default is 'ISO-8859-1'.` |
    | `on_bad_lines` | `(str)` | `What to do with bad lines encountered in the input files. Valid values are 'raise', 'warn', and 'skip'. Default is 'warn'.` |
    | `skiprows` | `(int or list-like)` | `Line numbers to skip (0-indexed) or number of lines to skip (int) at the start of the files. Default is 0.` |
    | `skipfooter` | `(int)` | `Number of lines to skip at the end of the files. Default is 0.` |
    | `key_columns` | `(list)` | `A list of column names to use as the primary keys for the comparison.` |
    | `ignore_columns` | `(list)` | `A list of column names to ignore during the comparison.` |
    | `report_type` | `(str)` | `The type of report to generate. Valid values are 'all', 'duplicate', or 'key_mismatch'. Default is 'all'.` |

    `Returns:`
    | *`Type`* | *`Description`* |
    | `pandas.DataFrame` | `A DataFrame containing the rows that are different between the two input DataFrames.` |

    Examples:
    | ${source_df} | Read CSV | path/to/source.csv |
    | ${target_df} | Read CSV | path/to/target.csv |
    | ${diff} | Compare All File Contents In Directories | ${source_df} | ${target_df} | key_columns=['col1', 'col2'] | ignore_columns=['col3'] |
    """

    logger.info('****************************************************************************************************')
    logger.info('PandasUtil Data Frame Comparison - Cell by Cell comparison with detailed mismatch report')
    logger.info('****************************************************************************************************')
    logger.info('Step-01 : Based on file format create the data frames with delimiter(sep)')

    source_df = create_dataframe_from_file(source_file_path_name, delimiter, has_header, width, colspecs, column_names,
                                           dtypes, encoding, on_bad_lines, skiprows, skipfooter)
    target_df = create_dataframe_from_file(target_file_path_name, delimiter, has_header, width, colspecs, column_names,
                                           dtypes, encoding, on_bad_lines, skiprows, skipfooter)

    # Store total records in source and target df
    total_target = round(len(source_df))
    total_source = round(len(target_df))
    total_mismatch = total_target - total_source

    logger.info('Step-02 : Remove the columns based on ignore columns list')

    # If ignore columns are specified, remove those columns from comparison
    if ignore_columns:
        for col in ignore_columns:
            # Check if the column exists in source_df and target_df and remove it
            if col in source_df.columns:
                source_df.drop(columns=col, inplace=True)
            if col in target_df.columns:
                target_df.drop(columns=col, inplace=True)

            # If col is an integer within valid range, remove by index
            elif isinstance(col, int) and 0 <= col < len(source_df.columns):
                source_df.drop(columns=source_df.columns[col], inplace=True)

            elif isinstance(col, int) and 0 <= col < len(target_df.columns):
                target_df.drop(columns=target_df.columns[col], inplace=True)

    logger.info('Step-03 : Check for duplicate rows in both source and target')

    # Check for column differences in source_df and target_df
    source_df_col_diff = set(source_df.columns) - set(target_df.columns)
    target_df_col_diff = set(target_df.columns) - set(source_df.columns)

    logger.debug(source_df_col_diff)
    source_df_col_diff = set(source_df.columns) - set(target_df.columns)

    # If key column is not specified then consider all columns except last column
    if len(key_columns) == 0:
        key_columns = source_df.columns.tolist()
        key_columns.pop()

    # Sort both target and source data frame
    source_df.sort_values(by=key_columns, ascending=True, inplace=True)
    target_df.sort_values(by=key_columns, ascending=True, inplace=True)

    # Check for duplicate key columns in target and source data frame
    source_df_dup_df = source_df[source_df[key_columns].duplicated()]
    target_df_dup_df = target_df[target_df[key_columns].duplicated()]

    logger.debug(source_df_dup_df)
    logger.debug(target_df_dup_df)
    logger.debug(len(source_df_dup_df))
    logger.debug(len(target_df_dup_df))

    total_target_dup = round(len(source_df_dup_df))
    total_source_dup = round(len(target_df_dup_df))

    logger.info('Step-04 : Remove duplicate records from source and target')

    # Get the duplicate key columns
    dup_target_df = source_df_dup_df.copy()
    dup_source_df = target_df_dup_df.copy()
    dup_target_df['file'] = 'target'
    dup_source_df['file'] = 'source'

    # Combine the duplicate keys from target and source data frame
    dup_cons_df = pd.concat([dup_target_df, dup_source_df], axis=0)
    dup_cons_df.reset_index(inplace=True)
    dup_cons_df.drop('index', axis=1, inplace=True)

    # Drop the duplicate columns before detailed comparison
    source_df.drop_duplicates(key_columns, inplace=True)
    target_df.drop_duplicates(key_columns, inplace=True)

    logger.debug(dup_target_df)
    logger.debug(dup_source_df)
    logger.debug(dup_cons_df)

    logger.info('Step-05 : Sort the source and target based on key columns and reset the index')

    # Sort source_df and target_df based on key columns and reset the index
    source_df.sort_values(by=key_columns, ascending=True, inplace=True)
    target_df.sort_values(by=key_columns, ascending=True, inplace=True)
    source_df.reset_index(inplace=True)
    target_df.reset_index(inplace=True)

    # Set the index based on key columns in source_df and target_df. Remove the default index column
    source_df = source_df.set_index(key_columns, drop=True, append=False, inplace=False, verify_integrity=True)
    target_df = target_df.set_index(key_columns, drop=True, append=False, inplace=False, verify_integrity=True)
    source_df = source_df.drop('index', axis=1)
    target_df = target_df.drop('index', axis=1)

    logger.info('Step-06 : Identify the rows matching based on key in both source and target')

    # Identify the rows matching based on key in both source_df and target_df
    merge_outer_df = pd.merge(source_df, target_df, how='outer', left_index=True, right_index=True, indicator='source')
    # merge_outer_df = pd.merge(source_df_key_columns, target_df_key_columns, how='outer', on=key_columns,
    # indicator='source')

    # Based on the key columns create key matched and mismatched details
    key_matched_df = merge_outer_df.loc[merge_outer_df['source'] == 'both'].copy()
    logger.debug(len(key_matched_df))
    key_mismatched_df = merge_outer_df.loc[merge_outer_df['source'] != 'both'].copy()
    key_mismatched_df = key_mismatched_df[['source']]

    # key_matched_df['source'] = 'Matched'
    # key_mismatched_df['source'] = 'MisMatched'
    logger.debug(key_mismatched_df)

    # Update the source column left_only to source and right_only to target
    # key_mismatched_df.loc[key_mismatched_df['source'] == 'left_only', 'source'] = 'source'

    target_key_mismatch = len(key_mismatched_df[key_mismatched_df.source == 'left_only'])
    source_key_mismatch = len(key_mismatched_df[key_mismatched_df.source == 'right_only'])

    # Create DataFrames for Data Only In Source and Data Only In Target
    data_only_in_source_df = source_df[~source_df.index.isin(target_df.index)].copy()
    data_only_in_target_df = target_df[~target_df.index.isin(source_df.index)].copy()

    logger.info('Step-07 : Create the summary report based on count diff, duplicate rows and key mismatches')

    only_in_source_count = len(data_only_in_source_df)
    only_in_target_count = len(data_only_in_target_df)

    # Extract source and target file names from file paths
    source_file_name = os.path.basename(source_file_path_name)
    target_file_name = os.path.basename(target_file_path_name)

    # Calculate count details for each column
    count_details = {
        'Source File Name': [source_file_name],  # Add source file name
        'Target File Name': [target_file_name],   # Add target file name
        'Source Total': [len(source_df)],
        'Target Total': [len(target_df)],
        'Total Key Matched': [len(key_matched_df)],
        'Total Keys & Data Matched': [0],
        'Total Keys & Data MisMatched': [0],
        'Total Data Breaks': [0],
        'Only in Source': [only_in_source_count],
        'Only in Target': [only_in_target_count],
        'Source Key Duplicates': [total_source_dup],
        'Target Key Duplicates': [total_target_dup],
        'Key Columns': [', '.join(key_columns)]  # Convert key_columns list to a comma-separated string
    }

    # Create the executive summary df
    exec_summary_df = pd.DataFrame.from_dict(count_details)
    logger.debug(exec_summary_df)

    logger.info('Step-08 : Remove the mismatched key values and proceed further in validation')

    source_df.drop(key_mismatched_df.loc[key_mismatched_df['source'] == 'left_only'].index, inplace=True)
    target_df.drop(key_mismatched_df.loc[key_mismatched_df['source'] == 'right_only'].index, inplace=True)

    # Step-08 to Step-12: Handle different report types
    if report_type == 'all':
        # Continue with all the comparison steps and generate all reports
        pass
    elif report_type == 'duplicate':
        # Return only the duplicate records report and exit the function
        logger.info('Step-09 : Comparison completed and generated info for reports(summary, duplicate')
        logger.info('************************************************************************************************')
        return exec_summary_df, dup_cons_df
    elif report_type == 'key_mismatch':
        # Return only the key mismatch report and exit the function
        logger.info('Step-09 : Comparison completed and generated info for reports(summary, key_mismatch')
        logger.info('************************************************************************************************')
        return exec_summary_df, key_mismatched_df, data_only_in_source_df, data_only_in_target_df
    else:
        # Invalid report type specified, raise an exception
        raise ValueError("Invalid 'report_type' specified. Valid values are 'all', 'duplicate', or 'key_mismatch'.")

    # Check if source_df and target_df are equal
    if source_df.equals(target_df):
        logger.info('No differences found between the DataFrames.')
        logger.info('************************************************************************************************')
        data_only_in_source_df = pd.DataFrame([])
        data_only_in_target_df = pd.DataFrame([])
        cell_comp_df = pd.DataFrame([])

        return exec_summary_df, dup_cons_df, key_matched_df, key_mismatched_df, data_only_in_source_df, \
            data_only_in_target_df, cell_comp_df

    logger.info('Step-09 : Started cell by cell comparison for key values that exist in both source and target')

    # Verify if columns in both source_df and target_df are same
    if not source_df.columns.equals(target_df.columns):
        logger.debug('Failed - Column mismatch determined')
        # Handle the column mismatch case here if needed
        # ...

    logger.info('Step-10 : Verify column data types in both the files, if not convert based on source')
    if not source_df.dtypes.equals(target_df.dtypes):
        logger.debug('Data Types are different, trying to convert')
        target_df = target_df.astype(source_df.dtypes)

    logger.info('Step-11 : Verify cell by cell data in both the data frame and generate mismatch report')

    # Identify where cells are different and generate a boolean mask
    diff_mask = (source_df != target_df) & ~(source_df.isnull() & target_df.isnull())

    # Special case: Treat 0 values in both DataFrames as matches
    zero_mask = (source_df == 0) & (target_df == 0)
    diff_mask = diff_mask | zero_mask

    # Check if diff_mask is empty (no differences found)
    if len(diff_mask) == 0:
        logger.info('Step-12 : No differences found between the DataFrames.')
        cell_comp_df = pd.DataFrame(columns=key_columns + ['Column', 'Target_Data', 'Source_Data', 'Compare_Result'])
    else:
        # Create a DataFrame with mismatched cells
        cell_comp_df = source_df.where(diff_mask).stack().reset_index()
        key_columns_names = key_columns if isinstance(key_columns, list) else [key_columns]
        cell_comp_df.columns = key_columns_names + ['Column', 'Source_Data']

        def get_index_value(row):
            if len(key_columns_names) > 1:
                return tuple(row[key] for key in key_columns_names)
            else:
                return row[key_columns_names[0]]

        # Apply the helper function to get index values
        cell_comp_df['Index_Value'] = cell_comp_df.apply(get_index_value, axis=1)

        # Use Index_Value to fetch Source_Data
        cell_comp_df['Target_Data'] = cell_comp_df.apply(
            lambda row: target_df.at[row['Index_Value'], row['Column']],
            axis=1
        )

        # Add a 'Compare_Result' column
        cell_comp_df['Compare_Result'] = np.where(cell_comp_df['Target_Data'] != cell_comp_df['Source_Data'],
                                                  'Mismatch', 'Match')
        # Assuming key_matched_df and cell_comp_df have the same index, you can get the unique index values
        unique_indices_in_key_matched = set(key_matched_df.index)
        unique_indices_in_cell_comp = set(cell_comp_df['Index_Value'])

        # Find the unique indices in key_matched_df that are not present in cell_comp_df
        matched_indices = unique_indices_in_key_matched.difference(unique_indices_in_cell_comp)

        # Drop the Index_Value column before returning
        cell_comp_df = cell_comp_df.drop(columns=['Index_Value'])

        # Calculate "Total Keys & Data MisMatched"
        total_keys_data_mismatch = int(len(key_matched_df)) - int(len(matched_indices))

        # Calculate "Total Data Breaks"
        total_data_breaks = int(len(cell_comp_df))

        # Calculate the count of unique keys that are matched in both key_matched_df and cell_comp_df
        total_key_data_matched = len(matched_indices)

        # Update the count details in the executive summary DataFrame
        exec_summary_df.loc[0, 'Total Keys & Data Matched'] = total_key_data_matched
        exec_summary_df.loc[0, 'Total Keys & Data MisMatched'] = total_keys_data_mismatch
        exec_summary_df.loc[0, 'Total Data Breaks'] = total_data_breaks

    logger.info('Step-12 : Comparison completed and generated info for reports(summary, keys mismatch, cell by cell)')
    logger.info('****************************************************************************************************')

    return exec_summary_df, dup_cons_df, key_matched_df, key_mismatched_df, data_only_in_source_df, \
        data_only_in_target_df, cell_comp_df


@keyword('Compare All Files In Directories')
def files_diff(src_dir: str, tgt_dir: str) -> pd.DataFrame:
    """
    Compare all files in source and target directories and return a DataFrame with the comparison results.

    `Args:`
    | *`Name`* | *`Type`* | *`Description`* |
    | `src_dir` | `str` | `The source directory to compare.` |
    | `tgt_dir` | `str` | `TThe target directory to compare.` |

    `Returns:`
    | *`Type`* | *`Description`* |
    | `pd.DataFrame` | `A DataFrame containing the comparison results, including file name, status, comments, and size in both directories.` |

    Examples:
    | ${result}= | Files Diff | ${source_dir} | ${target_dir} |
    | ${result}= | Files Diff | /path/to/source/dir | /path/to/target/dir |
    """

    logger.info(f"Step 1: Log the comparison directories")
    logger.info(f"Comparing files in {src_dir} and {tgt_dir}")

    common_files = find_common_files(src_dir, tgt_dir)

    match, mismatch, errors = compare_files(src_dir, tgt_dir, common_files)

    only_in_src = find_files_only_in_dir(src_dir, common_files)

    only_in_tgt = find_files_only_in_dir(tgt_dir, common_files)

    df = create_comparison_df(match, mismatch, errors, only_in_src, only_in_tgt, src_dir, tgt_dir)

    logger.info(f"Step 10: Created File Comparison Report - {len(df)} Files")
    return df


@keyword('Find Common Files In Directories')
def find_common_files(src_dir: str, tgt_dir: str) -> List[str]:
    """
    Find files that exist in both directories.

    `Args:`
    | *`Name`* | *`Type`* | *`Description`* |
    | `src_dir` | `str` | `The source directory.` |
    | `tgt_dir` | `str` | `The target directory.` |

    `Returns:`
    | *`Type`* | *`Description`* |
    | `List[Tuple[str, str]]` | `A list of tuples containing file paths, one for each file that exists in both directories.` |

    Examples:
    | ${result}= | Find Common Files | ${source_dir} | ${target_dir} |
    | ${result}= | Find Common Files | /path/to/source/dir | /path/to/target/dir |
    """
    logger.info(f"Step 2: Find common files in source and target directories")
    common_files = []
    for file in os.listdir(src_dir):
        if file in os.listdir(tgt_dir):
            common_files.append(file)
    return common_files


def compare_files(src_dir: str, tgt_dir: str, common_files: List[str]) -> Tuple[List[Tuple[str, int, int]],
List[Tuple[str, int, int, float]],
List[Tuple[str, str]]]:
    """
    Compare the files in the source and target directories.

    `Args:`
    | *`Name`* | *`Type`* | *`Description`* |
    | `src_dir` | `str` | `The source directory.` |
    | `tgt_dir` | `str` | `The target directory.` |
    | `files` | `list` | `A list of files to compare.` |

    `Returns:`
    | *`Type`* | *`Description`* |
    | `tuple` | `A tuple containing lists of matching files, mismatching files with percentage difference, and files with errors.` |

    Examples:
    | ${src_dir} | Set Variable | /path/to/source |
    | ${tgt_dir} | Set Variable | /path/to/target |
    | @{common_files} | Create List | file1.txt | file2.txt |
    | ${match_files} | ${mismatch_files} | ${error_files} | Compare Files | ${src_dir} | ${tgt_dir} | @{common_files} |
    | Log List | ${match_files} |
    | Log List | ${mismatch_files} |
    | Log List | ${error_files} |

    """
    match = []
    mismatch = []
    errors = []

    logger.info(f"Step 3: Compare each common file")
    for file in common_files:
        try:
            src_path = os.path.join(src_dir, file)
            tgt_path = os.path.join(tgt_dir, file)

            src_size = os.path.getsize(src_path)
            tgt_size = os.path.getsize(tgt_path)

            result = filecmp.cmpfiles(src_dir, tgt_dir, [file], shallow=False)
            if result[0]:
                match.append((file, src_size, tgt_size))
            else:
                diff_percentage = compare_file_contents(src_path, tgt_path)
                mismatch.append((file, src_size, tgt_size, diff_percentage))
        except Exception as e:
            errors.append((file, str(e)))

    return match, mismatch, errors


@keyword('Compare Files Using Diff')
def compare_file_contents(src_path: str, tgt_path: str) -> float:
    """
    Compares file contents using difflib and returns the percentage difference.

    Args:
        src_path (str): The source file path to compare.
        tgt_path (str): The target file path to compare.

    Returns:
        float: The percentage difference between the two files.

    Robot Framework Usage:
    | ${diff_percentage} | Compare File Contents | ${src_path} | ${tgt_path} |

    Examples:
    | ${diff_percentage} | Compare File Contents | /path/to/source/file.txt | /path/to/target/file.txt |
    """
    logger.info(f"Step 4: Compare file contents for {src_path} and {tgt_path}")
    with open(src_path, 'r') as f1, open(tgt_path, 'r') as f2:
        src_lines = f1.readlines()
        tgt_lines = f2.readlines()

    matcher = difflib.SequenceMatcher(None, src_lines, tgt_lines)
    diff_percentage = 100.0 - matcher.ratio() * 100.0

    return round(diff_percentage, 2)


def find_files_only_in_dir(directory: str, common_files: List[str]) -> List[str]:
    """
    Finds files that exist only in a directory and not in the common files list.

    Args:
        directory (str): The directory to search.
        common_files (List[str]): A list of common files.

    Returns:
        List[str]: A list of files that exist only in the directory.

    Robot Framework Usage:
        | *Arguments* |              |
        | directory   | ${dir_path}  |
        | common_files| @{common_files}|
        |             |              |
        | *Returns*   |              |
        |             | @{only_in_dir}|

    Examples:
        | ${common_files}= |  find common files | /path/to/source | /path/to/target |
        | ${only_in_source}= | find files only in dir | /path/to/source | ${common_files} |
        | ${only_in_target}= | find files only in dir | /path/to/target | ${common_files} |
    """
    logger.info(f"Step 4: Find files that exist only in {directory}")
    only_in_dir = []
    for file in os.listdir(directory):
        if file not in common_files:
            only_in_dir.append(file)
    return only_in_dir


@keyword("Create Comparison Dataframe")
# @keyword("Create Comparison Dataframe")
def create_comparison_df(match: List[Tuple[str, int, int]],
                         mismatch: List[Tuple[str, int, int, float]],
                         errors: List[Tuple[str, str]],
                         only_in_src: List[str],
                         only_in_tgt: List[str],
                         src_dir: str,
                         tgt_dir: str) -> pd.DataFrame:
    """
    Creates a DataFrame containing the comparison results.

    Args:
        match (List[Tuple[str, int, int]]): A list of matching files and their sizes.
        mismatch (List[Tuple[str, int, int, float]]): A list of mismatching files, their sizes, and the percentage difference.
        errors (List[Tuple[str, str]]): A list of files with errors and the error message.
        only_in_src (List[str]): A list of files only in the source directory.
        only_in_tgt (List[str]): A list of files only in the target directory.
        src_dir (str): Path to the source directory.
        tgt_dir (str): Path to the target directory.

    Returns:
        pd.DataFrame: A DataFrame containing the comparison results, including file name, status, comments, and size in both directories.
    """
    logger.info(f"Step 4: Create comparison DataFrame")
    data = []

    # Add matching files
    for file, src_size, tgt_size in match:
        data.append({"FileName": file,
                     "Status": "MATCH",
                     "Comments": "",
                     "Common_File": "Yes",
                     "Src_Size": src_size,
                     "Tgt_Size": tgt_size,
                     "Diff_Percentage": ""})

    # Add mismatching files
    for file, src_size, tgt_size, diff_percentage in mismatch:
        data.append({"FileName": file,
                     "Status": "MISMATCH",
                     "Comments": f"Percentage Difference: {diff_percentage:.2f}%",
                     "Common_File": "Yes",
                     "Src_Size": src_size,
                     "Tgt_Size": tgt_size,
                     "Diff_Percentage": diff_percentage})

    # Add files with errors
    for file, error in errors:
        data.append({"FileName": file,
                     "Status": "ERROR",
                     "Comments": error,
                     "Common_File": "Yes",
                     "Src_Size": "",
                     "Tgt_Size": "",
                     "Diff_Percentage": ""})

    # Add files only in source directory
    for file in only_in_src:
        data.append({"FileName": file,
                     "Status": "ONLY IN SRC",
                     "Comments": "",
                     "Common_File": "No",
                     "Src_Size": os.path.getsize(os.path.join(src_dir, file)),
                     "Tgt_Size": "",
                     "Diff_Percentage": ""})

    # Add files only in target directory
    for file in only_in_tgt:
        data.append({"FileName": file,
                     "Status": "ONLY IN TGT",
                     "Comments": "",
                     "Common_File": "No",
                     "Src_Size": "",
                     "Tgt_Size": os.path.getsize(os.path.join(tgt_dir, file)),
                     "Diff_Percentage": ""})

    df = pd.DataFrame(data, columns=["FileName", "Common_File", "Src_Size", "Tgt_Size", "Diff_Percentage", "Status",
                                     "Comments"])

    return df


@keyword('Compare All Files In Directories With Diffs')
def files_diff_with_diffs(src_dir: str, tgt_dir: str) -> None:
    """
    Compare all files in source and target directories and print the comparison results with diffs for matching files.

    `Args:`
    | *`Name`* | *`Type`* | *`Description`* |
    | `src_dir` | `str` | `The source directory to compare.` |
    | `tgt_dir` | `str` | `TThe target directory to compare.` |

    `Returns:`
    | `None` |  |

    Examples:
    | Files Diff With Diffs | ${source_dir} | ${target_dir} |
    | Files Diff With Diffs | /path/to/source/dir | /path/to/target/dir |
    """

    logger.info(f"Step 0: Starting comparison of files in {src_dir} and {tgt_dir}")

    # Call files_diff to get a dataframe of comparison results
    df = files_diff(src_dir, tgt_dir)

    # Loop through the matching files and print diffs
    for _, row in df[df['Status'] == 'Match'].iterrows():
        src_file = os.path.join(src_dir, row['File Name'])
        tgt_file = os.path.join(tgt_dir, row['File Name'])
        df_diff(src_file, tgt_file)


def replace_values_in_string(input_string, value_dict):
    """
    Replace values in a string based on a provided dictionary.

    Args:
    | *`Name`* | *`Type`* | *`Description`* |
    | `input_string` | `str` | `The input string to be modified.` |
    | `value_dict` | `dict` | `A dictionary containing keys (values to be replaced) and corresponding values.` |

    Returns:
    | *`Type`* | *`Description`* |
    | `str` | `Modified string.` |
    """
    for key, value in value_dict.items():
        input_string = input_string.replace(f"'~{key}'", f"'{value}'")
    return input_string


@keyword("Get File Format Using ICD")
def get_file_format_using_icd(icd_in_db: str, query_file_path: str = None, config_file_path: str = None,
                              db_config_name: str = None, replace_value_dict: dict = None, icd_config_path: str = None):
    """
    Get the file format using an ICD configuration.

    Args:
    | Name              | Type | Description                                       |
    |-------------------|------|---------------------------------------------------|
    | icd_in_db         | str  | Indicates whether the ICD configuration is in a database ('yes') or a file. |
    | query_file_path   | str  | The path to the query file if 'icd_in_db' is 'yes'. |
    | config_file_path  | str  | The path to the database configuration file if 'icd_in_db' is 'yes'. |
    | db_config_name    | str  | The name of the database configuration if 'icd_in_db' is 'yes'. |
    | icd_config_path   | str  | The path to the ICD configuration file if 'icd_in_db' is 'no'. |

    Returns:
    | Name           | Type           | Description                                     |
    |----------------|----------------|-------------------------------------------------|
    | colspecs       | list of tuples | List of colspecs as (start_pos, end_pos).        |
    | widths         | list of int    | List of field widths.                           |
    | dtypes         | dict           | Dictionary of field names and corresponding data types. |
    | column_names   | list of str    | List of column names.                           |

    Examples:
    | ${colspecs} | ${widths} | ${data_types} | ${column_names} | = | Get File Format Using ICD | /path/to/icd_config.xlsx |
    """
    colspecs = []
    widths = []
    dtypes = {}
    column_names = []
    key_columns = []

    if icd_in_db.lower() == 'yes':
        logger.info(f"Step-01: Reading ICD configuration from DB")
        try:
            query = RFDBUtils.get_query_from_file(query_file_path)
            query = replace_values_in_string(query, replace_value_dict)
            icd_df = RFDBUtils.execute_query(query=query, config_file_path=config_file_path,
                                             database_config_name=db_config_name)
            # Filter rows where unique_key_field is 'Yes'
            key_columns = icd_df[icd_df['unique_key_field'] == 'Y']['field_name'].tolist()

        except Exception as e:
            logger.error(f"Error reading ICD configuration: {e}")
            return None, None, None, None
    else:
        logger.info(f"Step-01: Reading ICD configuration from '{icd_config_path}'")
        try:
            icd_df = pd.read_excel(icd_config_path, sheet_name=0)  # Read the first sheet
            key_columns = icd_df[icd_df['unique_key_field'] == 'Y']['field_name'].tolist()
        except Exception as e:
            logger.error(f"Error reading ICD configuration: {e}")
            return None, None, None, None

        if not all(col in icd_df.columns for col in ['field_name', 'mandatory', 'datatype', 'field_length',
                                                     'start_position', 'end_position']):
            logger.error("ICD configuration is not as per format. Required columns are: "
                         "'field_name', 'mandatory', 'datatype', 'field_length', 'start_position', 'end_position'")
            return None, None, None, None

    for _, row in icd_df.iterrows():
        start_pos = row['start_position'] - 1  # Adjust to 0-index
        end_pos = row['end_position']
        length = row['field_length']
        dtypes = row['datatype']
        field_name = row['field_name']

        colspecs.append((start_pos, end_pos))
        widths.append(length)

        # Map ICD data type to Pandas data type
        # if dtypes.startswith('Varchar'):
        #     dtypes[field_name] = 'str'
        # elif dtypes.startswith('Integer'):
        #     dtypes[field_name] = 'int'
        # elif dtypes.startswith('Float'):
        #     dtypes[field_name] = 'float'

        column_names.append(field_name)

    if any(pd.isna(start) or pd.isna(end) for start, end in colspecs):
        colspecs = None
    dtypes = None

    if icd_in_db.lower() == 'yes':
        logger.info("Step-02: ICD configuration successfully processed")
        return colspecs, widths, dtypes, column_names, key_columns
    else:
        logger.info("Step-02: ICD configuration successfully processed")
        return colspecs, widths, dtypes, column_names, key_columns


def consolidate_execution_summary(results_folder_path, test_data_csv):
    """
    Consolidate execution summary for tests marked as "tbe" (To Be Executed).

    This function reads test data from a CSV file, filters tests marked as "tbe", and consolidates execution summary
    data from each test. It also extracts test statuses from associated output XML files.

    `Args:`
        | `results_folder_path` | `str` | The path to the folder containing test results. |
        | `test_data_csv` | `str` | The path to the test data CSV file. |

    `Returns:`
        | `pd.DataFrame` | The consolidated DataFrame containing execution summary. |
    """
    # Read the test_data.csv file into a DataFrame
    test_data_df = pd.read_csv(test_data_csv)

    # Filter rows where tbe is "Yes"
    tbe_yes_tests = test_data_df[test_data_df["tbe"] == "Yes"]

    # Initialize an empty DataFrame to store the consolidated data
    consolidated_df = pd.DataFrame()

    step = 1  # Initialize step counter

    for test_name in tbe_yes_tests["test_name"]:
        logger.info(f"Step - {step}: Processing test: {test_name}")
        step += 1

        # Define the path to the Overall Count Statistics.csv file for each test
        summary_file_path = os.path.join(results_folder_path, test_name, "Overall Count Statistics.csv")

        # Check if the file exists
        if os.path.exists(summary_file_path):
            logger.info(f"Step - {step}: Loading summary data for test: {test_name}")
            step += 1

            # Load the data from the CSV file into a DataFrame
            summary_df = pd.read_csv(summary_file_path)

            # Add 'Test Name' column to the summary DataFrame
            summary_df['Test Name'] = test_name

            # Determine status based on conditions
            conditions = (
                (summary_df['Total Keys & Data Matched'] < summary_df['Source Total']) |
                (summary_df['Total Keys & Data Matched'] < summary_df['Target Total'])
            )
            summary_df['Status'] = 'FAIL' if conditions.any() else 'PASS'

            # Concatenate the data to the consolidated DataFrame
            consolidated_df = pd.concat([consolidated_df, summary_df], ignore_index=True)
        else:
            logger.info(f"Step - {step}: Summary file not found for test: {test_name}")
            step += 1

    # Reorder the columns
    consolidated_df = consolidated_df[['Test Name', 'Status'] + [col for col in consolidated_df if col not in ['Test Name', 'Status']]]

    return consolidated_df

