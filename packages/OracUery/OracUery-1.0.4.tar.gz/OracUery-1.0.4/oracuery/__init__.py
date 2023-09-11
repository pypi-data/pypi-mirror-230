# Import necessary functions and classes from the package modules
from .oracuery import create_table_query, add_data_query, desc_table, select_query, select_column_query, select_raw_query

# Define what should be imported when using "from oracuery import *"
__all__ = [
    'create_table_query',
    'add_data_query',
    'desc_table',
    'select_query',
    'select_column_query',
    'select_raw_query',
]

# Optional package-level initialization code can be placed here

# For example, if you want to print a message when the package is imported:
# print("oracuery package is being initialized")

# It's common to include version information in the package
__version__ = '1.2.5'

# Additional package-level variables or configuration can be defined here

# If your package contains other modules, you can import them here
# For example, if you have a module named "helpers" in the same directory:
# from . import helpers
