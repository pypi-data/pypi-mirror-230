import pandas as pd
import sqlite3
import os
import time

class sequelframe:
    def __init__(self, file_path , table_name = "data"):
        # Infer file type from extension
        file_extension = os.path.splitext(file_path)[1]
        
        self.table_name = table_name
        # Read the file using pandas
        if file_extension == '.csv':
            self.df = pd.read_csv(file_path)
        elif file_extension in ['.xls', '.xlsx']:
            self.df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file type. Only CSV and Excel files are supported.")
        
        # Save the dataframe to SQLite with a unique name
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        timestamp = int(time.time())  # Getting the current timestamp
        self.db_name = f"{base_name}_{timestamp}.sqlite"  # Appending timestamp to ensure uniqueness
        self.conn = sqlite3.connect(self.db_name)
        self.df.to_sql(self.table_name, self.conn, if_exists='replace', index=False)
    
    def runsql(self, query):
        result = pd.read_sql(query, self.conn)
        print(result)
        return result

    
    def show(self):
        # Display all data from the database
        return self.runsql('SELECT * FROM data')

    def kill(self):
        # Close the connection
        self.conn.close()
        # Remove the SQLite database file
        os.remove(self.db_name)

    def __del__(self):
        # Just to make sure connection is closed if not already
        if self.conn:
            self.conn.close()
