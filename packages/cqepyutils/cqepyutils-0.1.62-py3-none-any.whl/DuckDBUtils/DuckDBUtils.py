import duckdb
import pandas as pd
import os
import logging
import time

# Setting up logging
logging.basicConfig(level=logging.INFO)

# Declare variables
DATABASE = ':memory:'
# SRC_PATH = 'C:/Users/ranji/OneDrive/PycharmProjects/pythontest/src/5m Sales Records.csv'
# TRG_PATH = 'C:/Users/ranji/OneDrive/PycharmProjects/pythontest/trg/5m Sales Records.csv'
# PRIMARY_KEYS = ['Order Date']
SRC_PATH = 'C:/Users/ranji/OneDrive/PycharmProjects/pythontest/src/Org.csv'
TRG_PATH = 'C:/Users/ranji/OneDrive/PycharmProjects/pythontest/trg/Org.csv'
PRIMARY_KEYS = ['Organization_Id']

MAPPING_FILE = 'IGP_ICD_Mapping.csv'
TABLE_SRC = 'table_src'
TABLE_TRG = 'table_trg'
OUTPUT_EXCEL = 'Results/comparison_results.xlsx'

# Use a disk-based database instead of in-memory
# DATABASE = 'C:/Users/ranji/OneDrive/PycharmProjects/pythontest/results/my_duckdb_database.db'
# Declare variables
logging.info('Variables declared')


def read_fixed_length_file(file_path, structure):
    # Read a fixed-length .dat file and return a list of dictionaries
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            row = {}
            for start, end, column_name in structure:
                row[column_name] = line[start:end].strip()
            data.append(row)
    return data


def load_data_into_duckdb(file_path, table_name):
    # Load data from a file into DuckDB based on its format
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.dat':
        # Read the structure from the Mapping.csv file
        mapping_df = pd.read_csv(MAPPING_FILE)
        # Trim spaces from the field_name column
        mapping_df['IGP Base Field'] = mapping_df['IGP Base Field'].str.strip()
        column_names = mapping_df['IGP Base Field'].tolist()
        structure = list(zip(mapping_df["'Start Position'"], mapping_df['End Position'], column_names))
        data = read_fixed_length_file(file_path, structure)
        conn.register(table_name, pd.DataFrame(data, columns=column_names))
    elif extension == '.csv':
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}')")
    elif extension == '.xml':
        data = pd.read_xml(file_path)
        conn.register(table_name, data)
    elif extension == '.json':
        data = pd.read_json(file_path)
        conn.register(table_name, data)
    else:
        raise ValueError(f"Unsupported file format: {extension}")
    # Return the column names for the loaded table
    column_info = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [col[1] for col in column_info]


# Create a connection to an in-memory DuckDB instance
conn = duckdb.connect(database=DATABASE, read_only=False)

# Load the data into DuckDB based on file format
columns_src_names = load_data_into_duckdb(SRC_PATH, TABLE_SRC)
columns_trg_names = load_data_into_duckdb(TRG_PATH, TABLE_TRG)

# Define keys string for SQL queries
# keys_str = ' AND '.join([f"a.{key} = b.{key}" for key in PRIMARY_KEYS])
keys_str = ' AND '.join([f'a."{key}" = b."{key}"' for key in PRIMARY_KEYS])

# List of columns to compare excluding primary keys
compare_columns = [col for col in columns_src_names if col not in PRIMARY_KEYS]

# Data breaks
start_time = time.time()
total_data_break_query = f"""
SELECT a.*, b.*
FROM {TABLE_SRC} AS a
LEFT JOIN {TABLE_TRG} AS b ON ({keys_str})
"""
total_data_break_data = conn.execute(total_data_break_query).fetchall()
logging.info(f"Total Data Break Query completed in {time.time() - start_time} seconds.")

# Determine the indices for the source and target columns
src_indices = [columns_src_names.index(col) for col in compare_columns]
trg_indices = [columns_trg_names.index(col) + len(columns_src_names) for col in compare_columns]

# Prepare the data for CSV
total_data_break = []
for row in total_data_break_data:
    mismatched_columns = {}
    for key in PRIMARY_KEYS:
        key_index = columns_src_names.index(key)
        mismatched_columns[key] = row[key_index]
    for idx, col in enumerate(compare_columns):
        src_value = row[src_indices[idx]]
        # Check if the target value exists
        if trg_indices[idx] < len(row):
            trg_value = row[trg_indices[idx]]
        else:
            trg_value = None  # Set to None if target value doesn't exist
        # Check for mismatch and capture the column name and differences
        if src_value != trg_value:
            mismatched_columns[f"{col}_Expected"] = src_value
            mismatched_columns[f"{col}_Actual"] = trg_value
    if len(mismatched_columns) > len(PRIMARY_KEYS):
        total_data_break.append(mismatched_columns)

# Write the data to CSV
pd.DataFrame(total_data_break).to_csv('total_data_break.csv', index=False)

# Only in Source
start_time = time.time()
only_in_source_query = f"""
SELECT a.*
FROM {TABLE_SRC} AS a
LEFT JOIN {TABLE_TRG} AS b ON ({keys_str})
WHERE b.{PRIMARY_KEYS[0]} IS NULL
"""
only_in_source = conn.execute(only_in_source_query).fetchall()
logging.info(f"Only in Source Query completed in {time.time() - start_time} seconds.")
pd.DataFrame(only_in_source, columns=columns_src_names).to_csv("only_in_source.csv", index=False)

# Only in Target
start_time = time.time()
only_in_target_query = f"""
SELECT b.*
FROM {TABLE_TRG} AS b
LEFT JOIN {TABLE_SRC} AS a ON ({keys_str})
WHERE a.{PRIMARY_KEYS[0]} IS NULL
"""
only_in_target = conn.execute(only_in_target_query).fetchall()
logging.info(f"Only in Target Query completed in {time.time() - start_time} seconds.")
pd.DataFrame(only_in_target, columns=columns_trg_names).to_csv("only_in_target.csv", index=False)

# Compute metrics and write to separate CSVs
keys_str_no_alias = ', '.join(PRIMARY_KEYS)

# Source Key Duplicate
start_time = time.time()
source_key_duplicate_query = f"""
SELECT *
FROM {TABLE_SRC}
WHERE ({keys_str_no_alias}) IN
    (SELECT {keys_str_no_alias}
     FROM {TABLE_SRC}
     GROUP BY ({keys_str_no_alias})
     HAVING COUNT(*) > 1)
"""

source_key_duplicate = conn.execute(source_key_duplicate_query).fetchall()
logging.info(f"Source Key Duplicate Query completed in {time.time() - start_time} seconds.")
pd.DataFrame(source_key_duplicate, columns=columns_src_names).to_csv('source_key_duplicate.csv', index=False)

# Target Key Duplicate
start_time = time.time()
target_key_duplicate_query = f"""
SELECT *
FROM {TABLE_TRG}
WHERE ({keys_str_no_alias}) IN
    (SELECT {keys_str_no_alias}
     FROM {TABLE_TRG}
     GROUP BY ({keys_str_no_alias})
     HAVING COUNT(*) > 1)
"""
target_key_duplicate = conn.execute(target_key_duplicate_query).fetchall()
logging.info(f"Target Key Duplicate Query completed in {time.time() - start_time} seconds.")
pd.DataFrame(target_key_duplicate, columns=columns_trg_names).to_csv('target_key_duplicate.csv', index=False)

# Metrics for the summary
source_total = conn.execute(f"SELECT COUNT(*) FROM {TABLE_SRC}").fetchone()[0]
target_total = conn.execute(f"SELECT COUNT(*) FROM {TABLE_TRG}").fetchone()[0]
total_key_matched = \
conn.execute(f"SELECT COUNT(*) FROM {TABLE_SRC} AS a JOIN {TABLE_TRG} AS b ON ({keys_str})").fetchone()[0]
only_in_source_count = len(only_in_source)
only_in_target_count = len(only_in_target)

# Detect duplicates in source and target based on primary keys
source_key_duplicate_count = conn.execute(f"SELECT COUNT(DISTINCT {', '.join(PRIMARY_KEYS)}) FROM {TABLE_SRC}").fetchone()[0]
target_key_duplicate_count = conn.execute(f"SELECT COUNT(DISTINCT {', '.join(PRIMARY_KEYS)}) FROM {TABLE_TRG}").fetchone()[0]

# Calculate total data breaks
total_data_break_count = len(total_data_break)

# Create summary dictionary
summary_data = {
    'Source Total': source_total,
    'Target Total': target_total,
    'Total Data Breaks': total_data_break_count,
    'Only in Source': only_in_source_count,
    'Only in Target': only_in_target_count,
    'Source Key Duplicate': source_key_duplicate_count,
    'Target Key Duplicate': target_key_duplicate_count
}

# Write the summary data to CSV
pd.DataFrame([summary_data]).to_csv("summary.csv", index=False)
