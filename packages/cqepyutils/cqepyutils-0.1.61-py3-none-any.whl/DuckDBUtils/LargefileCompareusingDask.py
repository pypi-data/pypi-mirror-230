import duckdb
import pandas as pd
import os, time
import logging
import csv
import dask.dataframe as dd

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Use a disk-based database instead of in-memory
DATABASE = 'C:/Users/ranji/OneDrive/PycharmProjects/pythontest/results/my_duckdb_database.db'
# Declare variables
SRC_PATH = 'C:/Users/ranji/OneDrive/PycharmProjects/pythontest/src/5m Sales Records.csv'
TRG_PATH = 'C:/Users/ranji/OneDrive/PycharmProjects/pythontest/trg/5m Sales Records.csv'
TABLE_SRC = 'table_src'
TABLE_TRG = 'table_trg'
PRIMARY_KEYS = ['Order Date']
logging.info('Variables declared')


def load_data_into_duckdb(file_path, table_name):
    """Load data from a file into DuckDB based on its format"""
    # Drop the table if it already exists
    conn.execute(f"DROP TABLE IF EXISTS {table_name}")

    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.csv':
        temp_table_name = table_name + '_temp'
        conn.execute(f"DROP TABLE IF EXISTS {temp_table_name}") # Drop the temporary table if it already exists
        conn.execute(f"CREATE TABLE {temp_table_name} AS SELECT * FROM read_csv_auto('{file_path}')")
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {temp_table_name}")
        conn.execute(f"DROP TABLE {temp_table_name}") # Drop the temporary table
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

# Dictionary to store column comparison results
column_differences = {}

# Compare columns using hashes
start_time = time.time()
for col in columns_src_names:
    col_quoted = f'"{col}"' if ' ' in col else col
    src_data = conn.execute(f"SELECT {col_quoted} FROM {TABLE_SRC} ORDER BY {col_quoted}").fetchall()
    trg_data = conn.execute(f"SELECT {col_quoted} FROM {TABLE_TRG} ORDER BY {col_quoted}").fetchall()

    src_hash = hash(str(src_data))
    trg_hash = hash(str(trg_data))

    if src_hash != trg_hash:
        mismatched_rows = conn.execute(
            f"SELECT COUNT(*) FROM {TABLE_SRC} AS a JOIN {TABLE_TRG} AS b ON ({keys_str}) WHERE a.{col_quoted} != b.{col_quoted}").fetchone()[
            0]
        total_rows = conn.execute(f"SELECT COUNT(*) FROM {TABLE_SRC}").fetchone()[0]
        percentage_difference = (mismatched_rows / total_rows) * 100
        column_differences[col] = percentage_difference

# Output the column differences to CSV
with open('total_data_breaks.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Column Name', 'Percentage Difference'])
    for col, diff in column_differences.items():
        writer.writerow([col, f"{diff:.2f}%"])

end_time = time.time()
time_taken = end_time - start_time # Calculate the time taken
logging.info(f'"Time Taken" comparison completed in {time_taken:.2f} seconds')
logging.info('Data breaks report saved as total_data_breaks.csv')

# Only in Source
start_time = time.time()

only_in_source_query = f"""
SELECT a.*
FROM {TABLE_SRC} AS a
LEFT JOIN {TABLE_TRG} AS b ON ({keys_str})
WHERE b."{PRIMARY_KEYS[0]}" IS NULL
"""

only_in_source = conn.execute(only_in_source_query).fetchall()
dd.from_pandas(pd.DataFrame(only_in_source, columns=columns_src_names), npartitions=10).compute().to_csv(
    "only_in_source.csv", index=False)
end_time = time.time()
time_taken = end_time - start_time # Calculate the time taken
logging.info(f'"Time Taken" comparison completed in {time_taken:.2f} seconds')
logging.info('Only in Source.csv')

# Only in Target
start_time = time.time()

only_in_target_query = f"""
SELECT b.*
FROM {TABLE_TRG} AS b
LEFT JOIN {TABLE_SRC} AS a ON ({keys_str})
WHERE a."{PRIMARY_KEYS[0]}" IS NULL
"""

only_in_target = conn.execute(only_in_target_query).fetchall()
dd.from_pandas(pd.DataFrame(only_in_target, columns=columns_trg_names), npartitions=10).compute().to_csv(
    "only_in_target.csv", index=False)

end_time = time.time()
time_taken = end_time - start_time # Calculate the time taken
logging.info(f'"Time Taken" comparison completed in {time_taken:.2f} seconds')
logging.info('Only in Target.csv')

# Source Key Duplicate
start_time = time.time()

source_key_duplicate_query = f"""
SELECT a.*
FROM {TABLE_SRC} AS a
JOIN (
    SELECT "{PRIMARY_KEYS[0]}"
    FROM {TABLE_SRC}
    GROUP BY "{PRIMARY_KEYS[0]}"
    HAVING COUNT(*) > 1
) AS b ON {' AND '.join([f'a."{key}" = b."{key}"' for key in PRIMARY_KEYS])}
"""

source_key_duplicate = conn.execute(source_key_duplicate_query).fetchall()
dd.from_pandas(pd.DataFrame(source_key_duplicate, columns=columns_src_names), npartitions=10).compute().to_csv(
    'source_key_duplicate.csv', index=False)

end_time = time.time()
time_taken = end_time - start_time # Calculate the time taken
logging.info(f'"Time Taken" comparison completed in {time_taken:.2f} seconds')
logging.info('Duplicate in Source.csv')

# Target Key Duplicate
start_time = time.time()

target_key_duplicate_query = f"""
SELECT a.*
FROM {TABLE_TRG} AS a
JOIN (
    SELECT "{PRIMARY_KEYS[0]}"
    FROM {TABLE_TRG}
    GROUP BY "{PRIMARY_KEYS[0]}"
    HAVING COUNT(*) > 1
) AS b ON {' AND '.join([f'a."{key}" = b."{key}"' for key in PRIMARY_KEYS])}
"""

target_key_duplicate = conn.execute(target_key_duplicate_query).fetchall()
dd.from_pandas(pd.DataFrame(target_key_duplicate, columns=columns_trg_names), npartitions=10).compute().to_csv(
    'target_key_duplicate.csv', index=False)

end_time = time.time()
time_taken = end_time - start_time # Calculate the time taken
logging.info(f'"Time Taken" comparison completed in {time_taken:.2f} seconds')
logging.info('Duplicate in Target.csv')

logging.info('Computed data for "Only in Source," "Only in Target," "Source Key Duplicate," and "Target Key Duplicate"')

# Compute metrics and write to separate CSVs
summary_data = {
    'Source Total': conn.execute(f"SELECT COUNT(*) FROM {TABLE_SRC}").fetchone()[0],
    'Target Total': conn.execute(f"SELECT COUNT(*) FROM {TABLE_TRG}").fetchone()[0],
    'Total Data Breaks (Columns)': len(column_differences),
    'Only in Source': len(only_in_source),
    'Only in Target': len(only_in_target),
    'Source Key Duplicate': len(source_key_duplicate),
    'Target Key Duplicate': len(target_key_duplicate)
}

# Convert the summary data to a DataFrame and save as CSV
pd.DataFrame([summary_data]).to_csv('summary.csv', index=False)
logging.info('Summary data computed and saved')

# Close the DuckDB connection
conn.close()
logging.info('DuckDB connection closed')
