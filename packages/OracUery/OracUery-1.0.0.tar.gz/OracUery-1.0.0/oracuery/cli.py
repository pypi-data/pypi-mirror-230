import argparse
import pandas as pd
from oracuery import (
    create_table_query,
    add_data_query,
    desc_table,
    select_query,
    select_column_query,
    select_raw_query,
)

class OracueryCLI:
    def __init__(self):
        self.parser = self.create_parser()
    
    def create_parser(self):
        """
        Create the command-line argument parser.

        Returns:
            argparse.ArgumentParser: The argument parser for the CLI.
        """
        parser = argparse.ArgumentParser(description="Oracuery Command Line Interface")
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Sub-command: create-table
        create_table_parser = subparsers.add_parser("create-table", help="Create a new table")
        create_table_parser.add_argument("table_name", help="Name of the table to create")
        create_table_parser.add_argument("input", help="Path to a CSV file with column definitions")
        create_table_parser.set_defaults(func=self.create_table)

        # Sub-command: add-data
        add_data_parser = subparsers.add_parser("add-data", help="Insert data into a table")
        add_data_parser.add_argument("table_name", help="Name of the table to insert data into")
        add_data_parser.add_argument("columns", help="Comma-separated list of columns to insert data into")
        add_data_parser.add_argument("input", help="Path to a CSV file with data to insert")
        add_data_parser.set_defaults(func=self.add_data)

        # Sub-command: desc
        desc_parser = subparsers.add_parser("desc", help="Describe the structure of a table")
        desc_parser.add_argument("table_name", help="Name of the table to describe")
        desc_parser.set_defaults(func=self.describe_table)

        # Sub-command: select
        select_parser = subparsers.add_parser("select", help="Select all rows from a table")
        select_parser.add_argument("table_name", help="Name of the table to select from")
        select_parser.set_defaults(func=self.select_all)

        # Sub-command: select-column
        select_column_parser = subparsers.add_parser("select-column", help="Select specific columns from a table")
        select_column_parser.add_argument("table_name", help="Name of the table to select from")
        select_column_parser.add_argument("columns", help="Comma-separated list of columns to select")
        select_column_parser.set_defaults(func=self.select_columns)

        # Sub-command: select-raw
        select_raw_parser = subparsers.add_parser("select-raw", help="Select data with a specified condition")
        select_raw_parser.add_argument("table_name", help="Name of the table to select from")
        select_raw_parser.add_argument("condition", help="The condition for selecting data")
        select_raw_parser.set_defaults(func=self.select_with_condition)

        return parser
    
    def create_table(self, args):
        """
        Generate a CREATE TABLE SQL query based on a CSV file with column definitions.

        Args:
            args: Parsed command-line arguments.
        """
        data = pd.read_csv(args.input)
        query = create_table_query(data, args.table_name)
        print(query)

    def add_data(self, args):
        """
        Generate an INSERT INTO SQL query based on a CSV file with data.

        Args:
            args: Parsed command-line arguments.
        """
        data = pd.read_csv(args.input)
        columns = args.columns.split(',')
        query = add_data_query(data, args.table_name, columns)
        print(query)

    def describe_table(self, args):
        """
        Generate a DESC SQL query to describe the structure of a table.

        Args:
            args: Parsed command-line arguments.
        """
        query = desc_table(args.table_name)
        print(query)

    def select_all(self, args):
        """
        Generate a SELECT * SQL query to select all rows from a table.

        Args:
            args: Parsed command-line arguments.
        """
        query = select_query(args.table_name)
        print(query)

    def select_columns(self, args):
        """
        Generate a SELECT SQL query to select specific columns from a table.

        Args:
            args: Parsed command-line arguments.
        """
        query = select_column_query(args.table_name, args.columns)
        print(query)

    def select_with_condition(self, args):
        """
        Generate a SELECT SQL query with a specified condition.

        Args:
            args: Parsed command-line arguments.
        """
        query = select_raw_query(args.table_name, args.condition)
        print(query)

    def run(self):
        """
        Parse command-line arguments and execute the corresponding command.
        """
        args = self.parser.parse_args()
        if hasattr(args, "func"):
            args.func(args)
        else:
            self.parser.print_help()

if __name__ == "__main__":
    cli = OracueryCLI()
    cli.run()
