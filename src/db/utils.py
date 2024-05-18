"""Small module for DB-related operations"""

import sqlite3
from datetime import datetime


def create_table(db_name):
    """
    Create a table in the specified SQLite database if it does not already exist.

    Parameters:
    - db_name (str): The name of the SQLite database.

    Returns:
    None

    Example:
    create_table('my_database.db')
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY,
            created_at DATETIME,
            parsed_text TEXT,
            parsed_data TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_data(db_name, raw_data, parsed_data):
    """
    Inserts data into the specified SQLite database.

    Parameters:
    - db_name (str): The name of the SQLite database.
    - raw_data (any): The raw data to be inserted.
    - parsed_data (any): The parsed data to be inserted.

    Returns:
    None

    Example:
    insert_data('my_database.db', raw_data, parsed_data)
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    now = datetime.now()
    c.execute(
        """
        INSERT INTO data (created_at, parsed_text, parsed_data) VALUES (?, ?, ?)
    """,
        (now, str(raw_data), str(parsed_data)),
    )
    conn.commit()
    conn.close()
