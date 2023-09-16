from robot.api import logger
from typing import List
from PandasUtils import RFPandasUtils
import pandas as pd
import os


class DynamicTestCases(object):
    """A Robot Framework test library to dynamically add test cases to the current suite."""
    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.current_suite = None

    def _start_suite(self, suite, result):
        self.current_suite = suite

    def add_test_case(self, name: str, doc: str, tags: List[str], kwname: str, **kwargs):
        """Adds a test case to the current suite.

        Args:
            | *Name*                  | *Type*   | *Description*                                                      |
            | `name`                  | `str`    | The test case name.                                                |
            | `doc`                   | `str`    | The documentation for the test case.                               |
            | `tags`                  | `str`    | Tags to be associated with the test case.                          |
            | `kwname`                | `str`    | The keyword to call.                                               |
            | `**kwargs`              | `str`    | Keyword arguments to be passed to the keyword.                     |

        Example:
        | Add Test Case | Example Test Case | This is a dynamic test case | ['smoke'] | My Keyword | arg1=value1 | arg2=value2 |
        """
        test_case = self.current_suite.tests.create(name=name, doc=doc, tags=tags)
        args = []
        for arg_name, arg_value in kwargs.items():
            args.append(f'{arg_name}={arg_value}')
        test_case.body.create_keyword(name=kwname, args=args)
        # self.suite.tests.append(test_case)

        logger.info(f"Added test case '{name}' with keyword '{kwname}' and keyword arguments:")
        for arg_name, arg_value in kwargs.items():
            logger.info(f"    {arg_name} = {arg_value}")

    @staticmethod
    def preprocess_kwargs(row):
        """
        Preprocesses keyword arguments based on ICD configuration.

        Args:
        | *Name*              | *Type*  | *Description*                                     |
        | `row`               | `dict`  | The row of data containing test case information. |

        Returns:
        | *Type* | *Description* |
        | `dict` | A dictionary containing preprocessed keyword arguments. |

        The method checks if the 'icd_available' value in the row is 'yes' or 'y'.
        If available, it extracts the 'icd_in_db', 'config_file_path', and 'db_config_name' from the row.
        It then reads the ICD configuration file based on the provided information.

        The method returns a dictionary with 'colspecs', 'dtypes', 'column_names', and 'key_columns' if applicable,
        otherwise an empty dictionary.

        `icd_in_db` (str, optional): Indicates whether the ICD configuration is in a database ('yes') or a file.
        `config_file_path` (str, optional): The path to the database configuration file if 'icd_in_db' is 'yes'.
        `db_config_name` (str, optional): The name of the database configuration if 'icd_in_db' is 'yes'.

        Example:
        | ${kwargs} = | Preprocess Kwargs | ${row} |
        """
        icd_available = row.get('icd_available', '').lower()
        icd_in_db = row.get('icd_in_db', '').lower()
        if icd_available in ['yes', 'y'] and icd_in_db.lower() == 'yes':
            config_file_path = row.get('config_file_path', '')
            query_file_path = row.get('query_file_path', '')
            db_config_name = row.get('db_config_name', '')
            replace_value_dict = {
                'service_id': row.get('service_id', ''),
                'service_ver': row.get('service_ver', '')
            }
            colspecs, _, dtypes, column_names, key_columns = \
                RFPandasUtils.get_file_format_using_icd(icd_in_db, query_file_path, config_file_path,
                                                        db_config_name, replace_value_dict)
            return {
                'colspecs': colspecs,
                'dtypes': dtypes,
                'column_names': column_names,
                'key_columns': key_columns
            }
        else:
            icd_config_path = row.get('icd_config_path', '')  # Extract the icd_config_path from the row
            if icd_config_path:
                colspecs, _, dtypes, column_names, key_columns = \
                    RFPandasUtils.get_file_format_using_icd(icd_in_db, icd_config_path=icd_config_path)
                return {
                    'colspecs': colspecs,
                    'dtypes': dtypes,
                    'column_names': column_names,
                    'key_columns': key_columns
                }
        return {}

    def read_test_data_and_add_test_cases(self, test_data_file_path: str):
        """Reads test data from a CSV or Excel file and adds test cases dynamically.

        Args:
            | *Name*             | *Type*   | *Description*                               |
            | `test_data_file_path` | `str`    | The path to the test data file (CSV or Excel). |

        The file should have the following columns:
        - test_name (*str*): Name of the test case.
        - test_scenario (*str*): Description of the test scenario.
        - test_tags (*str*): Comma-separated tags for categorization.
        - keyword (*str*): The keyword associated with the test.
        - tbe (*str*): 'Yes' or 'No' indicating whether the test case should be executed.
        - icd_config_path (*str*): The path to the ICD configuration file (if available).
        - Any additional columns ending with '_v' (*str*): Additional parameters for the test case.

        Example:
        | Read Test Data And Add Test Cases | /path/to/test_data.xlsx |
        """
        try:
            file_extension = os.path.splitext(test_data_file_path)[-1].lower()

            if file_extension == '.csv':
                df = pd.read_csv(test_data_file_path, dtype='str')
            elif file_extension == '.xlsx':
                df = pd.read_excel(test_data_file_path, dtype='str', sheet_name=0)
            else:
                raise ValueError("Unsupported file format. Supported formats are .csv and .xlsx.")

            # Filter rows based on values in the 'tbe' column
            filtered_df = df[df['tbe'].str.lower().isin(['yes', 'y'])]

            for _, row in filtered_df.iterrows():
                name = row.get('test_name', '')
                doc = row.get('test_scenario', '')
                tags = row.get('test_tags', '').split(',')
                kwname = row.get('keyword', '')

                kwargs = {col[:-2]: row[col] if pd.notna(row[col]) else None for col in filtered_df.columns if
                          col.endswith('_v')}
                kwargs.update(self.preprocess_kwargs(row))
                kwargs = {key: value for key, value in kwargs.items() if value is not None}

                self.add_test_case(name=name, doc=doc, tags=tags, kwname=kwname, **kwargs)

            logger.info(f"Successfully added test cases from '{test_data_file_path}'.")
        except Exception as e:
            logger.error(f"Error occurred while reading test data from '{test_data_file_path}': {e}")
