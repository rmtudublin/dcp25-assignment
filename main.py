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

def parse_abc_file(file_path, book_number):
    # a tune begins when programme encounters a line starting with "X:".

    tunes = []              # will store all parsed tunes
    current_tune = None     # will hold the tune currently being parsed
    abc_lines = []          # stores the full ABC text for the tune

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()   # remove newline characters

            # detect the start of a new tune (X: is ALWAYS the first line)
            
            if line.startswith("X:"):
                # if we were already parsing a tune, save it before starting a new one
                if current_tune:
                    current_tune["abc"] = "\n".join(abc_lines)   # store full ABC text
                    tunes.append(current_tune)                   # add completed tune to list

                # begin a new tune dictionary with default fields
                current_tune = {
                    "book_number": book_number,      # Which book the tune came from
                    "tune_index": line[2:].strip(),  # Value after "X:"
                    "title": None,
                    "tune_type": None,
                    "meter": None,
                    "unit_length": None,
                    "key_signature": None
                }

                abc_lines = [line]   # Reset ABC text collector for new tune
                continue             # Move to next line

           
            # ignore lines before the first X: 
            if current_tune is None:
                continue

           
            # from here, we are inside a tune → record the ABC body
            
            abc_lines.append(line)

            
            # identify and extract header fields
            
            if line.startswith("T:"):
                current_tune["title"] = line[2:].strip()
            elif line.startswith("R:"):
                current_tune["tune_type"] = line[2:].strip()
            elif line.startswith("M:"):
                current_tune["meter"] = line[2:].strip()
            elif line.startswith("L:"):
                current_tune["unit_length"] = line[2:].strip()
            elif line.startswith("K:"):
                current_tune["key_signature"] = line[2:].strip()

    # after the loop ends, store the last tune (if one was being parsed)

    if current_tune:
        current_tune["abc"] = "\n".join(abc_lines)
        tunes.append(current_tune)

    return tunes          # return list of all parsed tune dictionaries


# database setup functions (improved by AI)

def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect("tunes.db")


def setup_database():
    """
    Creates the 'tunes' table with all columns matching the parser.
    """
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS tunes;")
    
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



# this function goes through every folder to find .abc files and collects all tunes into a list

def load_all_abc_files(root_folder="abc_books"):

    all_tunes = []   #list to collect tunes from every file

    #walk through every folder and file inside abc_books/
    for root, _, files in os.walk(root_folder):
        folder = os.path.basename(root)   #get the name of the current folder
        if not folder.isdigit():
            continue  # skip non-numeric folders
        book_number = int(folder)
        #loop through every file in that folder
        for file in files:
            if not file.endswith('.abc'):
                continue  # only process .abc files
            path = os.path.join(root, file)
            # parse the file then returns a list of tune dictionaries
            tunes = parse_abc_file(path, book_number)
            #add those tunes to the main list
            all_tunes.extend(tunes)
    return all_tunes


    
# function to insert list of tunes into the database
def insert_tunes(tunes):
    conn = get_connection()
    cur = conn.cursor()

    for t in tunes:
        cur.execute("""
            INSERT INTO tunes 
            (book_number, tune_index, title, tune_type, meter, unit_length, key_signature, abc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t["book_number"],
            t["tune_index"],
            t["title"],
            t["tune_type"],
            t["meter"],
            t["unit_length"],
            t["key_signature"],
            t["abc"]
        ))

    conn.commit()
    conn.close()

#load dataframe from the database created earlier
def load_dataframe():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM tunes", conn)
    conn.close()
    return df

#functions to query the data

# this function allows userr to get all tunes from a specific book number
def get_tunes_by_book(df, book_number):
    return df[df["book_number"] == book_number]

# this function allows user to get all tunes of a specific type
def get_tunes_by_type(df, tune_type):
    return df[df["tune_type"].str.contains(tune_type, case=False, na=False)]

# this function allows user to search for the title of tunes
def search_tunes(df, term):
    return df[df["title"].str.contains(term, case=False, na=False)]

#function to select tune by key signature
def get_tunes_by_key(df, key_signature):
    return df[df["key_signature"].str.contains(key_signature, case=False, na=False)]

#function to count tunes per book
def count_tunes_per_book(df):
    return df.groupby("book_number")["id"].count()



#function to create user menu in terminal
def run_ui():
    df = load_dataframe()
    while True:
        print("\n Rory's Book of Tunes Database")
        print("1. Show tunes in a book")
        print("2. Show tunes by type")
        print("3. Have a title? Search tunes!")
        print("4. Looking for a tune with a particular key signature?")
        print("5. Count tunes per book")
        print("0. Quit")
        
        choice = input("Enter your choice: ")
        if choice == "1":
            book_number = int(input("Enter book number: "))
            result = get_tunes_by_book(df, book_number)
            print(result)
 
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    setup_database()
    tunes = load_all_abc_files()
    insert_tunes(tunes)
    run_ui()