import os 
import sqlite3
import pandas as pd



# sqlite connection function
def get_connection(db_path="tunes.db"):
    conn = sqlite3.connect(db_path)
    return conn

def setup_database():
    """
    Creates the 'tunes' table.
        
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tunes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_number INTEGER,
            title TEXT,
            tune_type TEXT,
            key_sig TEXT,
            abc_text TEXT
        )
    """)
    conn.commit()
    conn.close()


