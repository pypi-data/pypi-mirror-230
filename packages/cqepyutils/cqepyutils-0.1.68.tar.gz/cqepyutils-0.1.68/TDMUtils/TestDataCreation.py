import os
import logging
import random

# Define logging
# Create logger definition
logger = logging.getLogger('file_inflation.log')
logger.setLevel(logging.DEBUG)

# Create file handler which logs messages in log file
fh = logging.FileHandler('file_inflation.log')
fh.setLevel(logging.DEBUG)

# Create console handler with high level log messages in console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(ch)


def inflate_file(input_file: str, output_file: str, target_size_gb=2):
    """
    This method is used to inflate the size of a file by replicating its content.
    :param input_file: Path to the input file.
    :param output_file: Path to the output file.
    :param target_size_gb: Target size in GB. Default is 2GB.
    :return: None
    """
    logger.info('****************************************************************************************************')
    logger.info('File Inflation - Start')
    logger.info('****************************************************************************************************')

    # Calculate the size in bytes
    target_size_bytes = target_size_gb * (1024 ** 3)

    # Read the input file
    with open(input_file, 'r') as f:
        data = f.read()

    # Calculate how many times the data should be replicated
    replication_factor = target_size_bytes // len(data.encode('utf-8'))

    logger.info(f'Step-01 : Replicating data {replication_factor} times to achieve target size.')

    # Write the replicated data to the output file
    with open(output_file, 'w') as f:
        for _ in range(replication_factor):
            f.write(data)

    logger.info('****************************************************************************************************')
    logger.info('File Inflation - Complete')
    logger.info('****************************************************************************************************')


# Logging setup
logger = logging.getLogger('random_diff.log')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('random_diff.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)


def introduce_random_diff(input_file: str, output_file: str, num_changes: int = 10):
    """
    Introduce random differences in a file.
    :param input_file: Path to the original file.
    :param output_file: Path to the output file with differences.
    :param num_changes: Number of changes to introduce. Default is 10.
    :return: None
    """
    logger.info('****************************************************************************************************')
    logger.info('Introducing Random Differences - Start')
    logger.info('****************************************************************************************************')

    with open(input_file, 'r') as f:
        lines = f.readlines()

    for _ in range(num_changes):
        change_type = random.choice(['modify', 'delete', 'add'])
        index = random.randint(0, len(lines) - 1)

        if change_type == 'modify':
            lines[index] = f"MODIFIED: {lines[index]}"
            logger.info(f'Modified line {index + 1}')

        elif change_type == 'delete':
            del lines[index]
            logger.info(f'Deleted line {index + 1}')

        elif change_type == 'add':
            lines.insert(index, f"ADDED LINE: Random content {random.randint(0, 1000)}\n")
            logger.info(f'Added line after {index + 1}')

    with open(output_file, 'w') as f:
        f.writelines(lines)

    logger.info('****************************************************************************************************')
    logger.info('Introducing Random Differences - Complete')
    logger.info('****************************************************************************************************')

#
# # Usage
# input_file_path = "path_to_original_file.txt"
# output_file_path = "path_to_modified_file.txt"
# introduce_random_diff(input_file_path, output_file_path)