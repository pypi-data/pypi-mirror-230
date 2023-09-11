# ORACUERY

oracuery is a comprehensive Python module that simplifies database interaction by providing a set of powerful functions to generate SQL queries effortlessly. Whether you're working with databases in your web application, data analysis project, or any Python-based application, oracuery streamlines the process, saving you time and reducing the complexity of writing SQL queries.

## Features

- **Table Creation**: The ou.create_table_query(data, table_name) function allows you to generate SQL table creation queries dynamically. Specify column names, data types, and sizes using a Pandas DataFrame. This makes it easy to define your table schema programmatically.

- **Data Insertion**: With ou.add_data_query(data, table_name, columns), you can effortlessly generate SQL queries for inserting data into your tables. Simply provide your data in a Pandas DataFrame and specify the target table and columns.

- **Table Description**: Use ou.desc_table(table_name) to retrieve the structure of a table. This function generates an SQL query to describe the table's schema, helping you understand its structure at a glance.

- **Data Selection**: ou.select_query(table_name), ou.select_column_query(table_name, find), and ou.select_raw_query(table_name, condition) empower you to create SQL queries for selecting data from your tables. Fetch all rows, specific columns, or apply custom conditions with ease.

## Installation

You can install `oracuery` using pip:

```bash
pip install oracuery
