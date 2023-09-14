import csv
import os

primary_key = ["Weight(Pounds)"]
def load_csv_to_dict(filepath):
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        return {row['primary_key']: row for row in reader}


def binary_compare(value1, value2):
    return value1.encode() == value2.encode()


def compare_csv_files(src, trg):
    src_data = load_csv_to_dict(src)
    trg_data = load_csv_to_dict(trg)

    differences = []

    for key, src_row in src_data.items():
        trg_row = trg_data.get(key)
        if not trg_row:
            differences.append(f"Missing key {key} in target file.")
            continue

        for column, src_value in src_row.items():
            trg_value = trg_row[column]
            if not binary_compare(src_value, trg_value):
                differences.append(
                    f"Difference at key {key}, column {column}. Source: {src_value}, Target: {trg_value}")

    return differences


def write_diff_to_csv(differences, csv_path):
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Differences"])
        for diff in differences:
            writer.writerow([diff])



src = "C:/Users/ranji/Downloads/src/hw_200.csv"  # Update with the path to the first file
trg = "C:/Users/ranji/Downloads/trg/hw_200.csv"  # Sample file URL
csv_path = 'differences_report.csv'

differences = compare_csv_files(src, trg)

if differences:
    write_diff_to_csv(differences, csv_path)
    print(f"Differences written to {csv_path}.")
else:
    print("The files are identical.")
