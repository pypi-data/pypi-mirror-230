import duckdb
import pandas as pd
import os
import logging
import gc  # Importing garbage collection module
import csv

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Use a disk-based database instead of in-memory
DATABASE = 'C:/pythontest/results/my_duckdb_database.db'
# Declare variables
SRC_PATH = 'C:/pythontest/src/5m Sales Records.csv'
TRG_PATH = 'C:/pythontest/trg/5m Sales Records.csv'
MAPPING_FILE = 'IGP_ ICD Mapping.csv'
TABLE_SRC = 'table_src'
TABLE_TRG = 'table_trg'
OUTPUT_EXCEL = 'C:/pythontest/results/comparison_results.xlsx'
PRIMARY_KEYS = ['Order Date']

logging.info('Variables declared')


def read_fixed_length_file(file_path, structure):
    """Read a fixed-length .dat file and return a list of dictionaries."""
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            row = {}
            for start, end, column_name in structure:
                row[column_name] = line[start:end].strip()
            data.append(row)
    return data


logging.info('Function read_fixed_length_file defined')


def load_data_into_duckdb(file_path, table_name):
    """Load data from a file into DuckDB based on its format"""
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.dat':
        mapping_df = pd.read_csv(MAPPING_FILE)
        mapping_df['IGP Base Field'] = mapping_df['IGP Base Field'].str.strip()
        column_names = mapping_df['IGP Base Field'].tolist()
        structure = list(zip(mapping_df['Start Position'], mapping_df['End Position'], column_names))
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
        raise ValueError(f'Unsupported file format: {extension}')
    column_info = conn.execute(f'PRAGMA table_info({table_name})').fetchall()
    return [col[1] for col in column_info]


logging.info('Function load_data_into_duckdb defined')

# Create a connection to DuckDB
conn = duckdb.connect(database=DATABASE, read_only=False)
logging.info('Connected to DuckDB')

# Load the data into DuckDB based on file format
columns_src_names = load_data_into_duckdb(SRC_PATH, TABLE_SRC)
columns_trg_names = load_data_into_duckdb(TRG_PATH, TABLE_TRG)
logging.info('Data loaded into DuckDB')

# Define keys string for SQL queries
keys_str = ' AND '.join([f'a."{key}" = b."{key}"' if ' ' in key else f'a.{key} = b.{key}' for key in PRIMARY_KEYS])

# List of columns to compare excluding primary keys
compare_columns = [col for col in columns_src_names if col not in PRIMARY_KEYS]

# Compute source_total and target_total
source_total = conn.execute(f"SELECT COUNT(*) FROM {TABLE_SRC}").fetchone()[0]
target_total = conn.execute(f"SELECT COUNT(*) FROM {TABLE_TRG}").fetchone()[0]
logging.info(f'Source total: {source_total}, Target total: {target_total}')


# Data breaks
logging.info('Starting data breaks computation')

total_data_break_query = f"""
SELECT a.*, b.*
FROM {TABLE_SRC} AS a
LEFT JOIN {TABLE_TRG} AS b ON ({keys_str})
"""

total_data_break_data = conn.execute(total_data_break_query).fetchall()

# Determine the indices for the source and target columns
src_indices = [columns_src_names.index(col) for col in compare_columns]
trg_indices = [columns_trg_names.index(col) + len(columns_src_names) for col in compare_columns]

# Data breaks
logging.info('Starting data breaks computation')

total_data_break_query = f"""
SELECT a.*, b.*
FROM {TABLE_SRC} AS a
LEFT JOIN {TABLE_TRG} AS b ON ({keys_str})
"""

# Open a CSV file for writing
with open('total_data_break.csv', 'w', newline='') as csvfile:
    writer = None

    # Fetching results in chunks
    chunk_size = 1000
    result_set = conn.execute(total_data_break_query)
    while True:
        chunk = result_set.fetchmany(chunk_size)
        if not chunk:
            break

        # Process the chunk and prepare data breaks
        total_data_breaks_chunk = []
        for row in chunk:
            mismatched_columns = {}
            for key in PRIMARY_KEYS:
                key_index = columns_src_names.index(key)
                mismatched_columns[key] = row[key_index]

            for idx, col in enumerate(compare_columns):
                src_value = row[src_indices[idx]]
                if trg_indices[idx] < len(row):
                    trg_value = row[trg_indices[idx]]
                else:
                    trg_value = None

                if src_value != trg_value:
                    mismatched_columns[f"{col}_Expected"] = src_value
                    mismatched_columns[f"{col}_Actual"] = trg_value
                    logging.info('src not equal to trg')

            if len(mismatched_columns) > len(PRIMARY_KEYS):
                total_data_breaks_chunk.append(mismatched_columns)

        # Write the chunk to CSV
        if not writer:
            writer = csv.DictWriter(csvfile, fieldnames=total_data_breaks_chunk[0].keys())
            writer.writeheader()
        writer.writerows(total_data_breaks_chunk)

gc.collect()  # Trigger garbage collection
logging.info('Data breaks computation completed')


# Only in Source
only_in_source_query = f"""
SELECT a.*
FROM {TABLE_SRC} AS a
LEFT JOIN {TABLE_TRG} AS b ON ({keys_str})
WHERE b.{PRIMARY_KEYS[0]} IS NULL
"""

only_in_source = conn.execute(only_in_source_query).fetchall()
pd.DataFrame(only_in_source, columns=columns_src_names).to_csv("only_in_source.csv", index=False)

# Only in Target
only_in_target_query = f"""
SELECT b.*
FROM {TABLE_TRG} AS b
LEFT JOIN {TABLE_SRC} AS a ON ({keys_str})
WHERE a.{PRIMARY_KEYS[0]} IS NULL
"""

only_in_target = conn.execute(only_in_target_query).fetchall()
pd.DataFrame(only_in_target, columns=columns_src_names).to_csv("only_in_target.csv", index=False)

logging.info('Computed data for "Only in Source" and "Only in Target"')

# Compute metrics and write to separate CSVs
keys_str_no_alias = ', '.join(PRIMARY_KEYS)

# Source Key Duplicate
source_key_duplicate_query = f"""
SELECT a.*
FROM {TABLE_SRC} AS a
JOIN (
    SELECT {keys_str_no_alias}
    FROM {TABLE_SRC}
    GROUP BY ({keys_str_no_alias})
    HAVING COUNT(*) > 1
) AS b ON a.{PRIMARY_KEYS[0]} = b.{PRIMARY_KEYS[0]}
"""

source_key_duplicate = conn.execute(source_key_duplicate_query).fetchall()
pd.DataFrame(source_key_duplicate, columns=columns_src_names).to_csv('source_key_duplicate.csv', index=False)

# Target Key Duplicate
target_key_duplicate_query = f"""
SELECT a.*
FROM {TABLE_TRG} AS a
JOIN (
    SELECT {keys_str_no_alias}
    FROM {TABLE_TRG}
    GROUP BY ({keys_str_no_alias})
    HAVING COUNT(*) > 1
) AS b ON a.{PRIMARY_KEYS[0]} = b.{PRIMARY_KEYS[0]}
"""

target_key_duplicate = conn.execute(target_key_duplicate_query).fetchall()
pd.DataFrame(target_key_duplicate, columns=columns_trg_names).to_csv('target_key_duplicate.csv', index=False)

logging.info('Computed data for "Source Key Duplicate" and "Target Key Duplicate"')

# Create summary dictionary
summary_data = {
    'Source Total': source_total,
    'Target Total': target_total,
    'Columns with Differences': len(column_differences),
    'Only in Source': len(only_in_source),
    'Only in Target': len(only_in_target),
    'Source Key Duplicate': len(source_key_duplicate),
    'Target Key Duplicate': len(target_key_duplicate)
}

pd.DataFrame([summary_data]).to_csv('summary.csv', index=False)
logging.info('Summary data computed and saved')

# Close the DuckDB connection
conn.close()
logging.info('DuckDB connection closed')
