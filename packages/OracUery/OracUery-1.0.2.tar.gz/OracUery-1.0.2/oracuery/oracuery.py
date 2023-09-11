# Function to generate a CREATE TABLE query based on data and table name
def create_table_query(data, table_name):
    """
    Generate an SQL query for creating a new table based on provided column information.

    Args:
        data (DataFrame): A DataFrame containing column definitions.
        table_name (str): The name of the table to be created.

    Returns:
        str: The SQL query for creating the table.
    """
    query = f"CREATE TABLE {table_name} ("  # Initialize the CREATE TABLE query
    column_template = "{} {}[{}]"  # Define a template for column definition

    # Iterate through DataFrame rows to construct column definitions
    for _, row in data.iterrows():
        # Append each column definition to the query
        query += column_template.format(row["Column"], row["DataType"], row["Size"]) + ", "

    query = query.rstrip(", ") + ");"  # Remove trailing comma and close the query
    return query


# Function to generate an INSERT INTO query for adding data to a table
def add_data_query(data, table_name, columns):
    """
    Generate an SQL query for inserting data into a specified table.

    Args:
        data (DataFrame): A DataFrame containing the data to be inserted.
        table_name (str): The name of the table to insert data into.
        columns (list): A list of columns to insert data into.

    Returns:
        str: The SQL query for inserting data.
    """
    query = f"INSERT INTO {table_name}(" + ", ".join(columns) + ") VALUES"  # Initialize the INSERT INTO query
    temp = query
    rows = []

    # Iterate through DataFrame rows to construct rows of data
    for _, row in data.iterrows():
        row_values = "', '".join(str(row[value]) for value in columns)
        rows.append("('" + row_values + "')")

    query += f";\n{temp}".join(rows) + ";"  # Append data rows and close the query
    return query


# Function to generate a DESC query for describing a table's structure
def desc_table(table_name):
    """
    Generate an SQL query to retrieve the structure of a specified table.

    Args:
        table_name (str): The name of the table to describe.

    Returns:
        str: The SQL query for describing the table.
    """
    query = f"DESC {table_name}"  # Generate the DESC query
    return query


# Function to generate a SELECT * query for retrieving all rows from a table
def select_query(table_name):
    """
    Generate an SQL query to select all rows from a specified table.

    Args:
        table_name (str): The name of the table to retrieve data from.

    Returns:
        str: The SQL query for selecting all rows.
    """
    query = f"SELECT * FROM {table_name};"  # Generate the SELECT * query
    return query


# Function to generate a SELECT query for specific columns from a table
def select_column_query(table_name, find):
    """
    Generate an SQL query to retrieve specific columns from a specified table.

    Args:
        table_name (str): The name of the table to retrieve data from.
        find (str): The columns to retrieve.

    Returns:
        str: The SQL query for selecting specific columns.
    """
    query = f"SELECT {find} FROM {table_name};"  # Generate the SELECT query
    return query


# Function to generate a SELECT query with a specified condition
def select_raw_query(table_name, Condition):
    """
    Generate an SQL query with a specified condition to retrieve data from a table.

    Args:
        table_name (str): The name of the table to retrieve data from.
        Condition (str): The condition to apply in the query.

    Returns:
        str: The SQL query with the specified condition.
    """
    query = f"SELECT * FROM {table_name} where {Condition};"  # Generate the SELECT query with condition
    return query
