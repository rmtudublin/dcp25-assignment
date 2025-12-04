import os 
import sqlite3
import pandas as pd

# pandas display options for better readability in the console

# ensures all columns are displayed (not hidden with ...)
pd.set_option('display.max_columns', None)

# ensures rows don't wrap weirdly on wide terminals
pd.set_option('display.width', 1000)

# ensures long titles aren't cut off with ...
pd.set_option('display.max_colwidth', None)

# PARSING FUNCTIONS: reads an ABC file and extracts one or more tunes.




# database setup functions (improved by AI)

def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect()


def setup_database():
    """
    Creates the 'tunes' table with all columns matching the parser.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS tunes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_number INT,
            tune_index TEXT,
            title TEXT,
            tune_type TEXT,
            meter TEXT,
            unit_length TEXT,
            key_signature TEXT,
            abc TEXT
        );
    """)
    conn.commit()
    conn.close()

