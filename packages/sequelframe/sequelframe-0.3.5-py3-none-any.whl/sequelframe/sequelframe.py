import pandas as pd
import sqlite3
import os
import time

class sequelframe:
    def __init__(self, data , table_name = "data"):
        self.table_name = table_name
        
        # Check if the provided data is a pandas DataFrame
        if isinstance(data, pd.DataFrame):
            self.df = data
        # If data is a string, treat it as a file path
        elif isinstance(data, str):
            # Infer file type from extension
            file_extension = os.path.splitext(data)[1]
            
            # Read the file using pandas
            if file_extension == '.csv':
                self.df = pd.read_csv(data)
            elif file_extension in ['.xls', '.xlsx']:
                self.df = pd.read_excel(data)
            else:
                raise ValueError("Unsupported file type. Only CSV and Excel files are supported.")
        else:
            raise ValueError("Data type not understood. Please provide a pandas DataFrame or a valid file path.")
        
        # Save the dataframe to SQLite with a unique name
        base_name = 'temp' if isinstance(data, pd.DataFrame) else os.path.splitext(os.path.basename(data))[0]
        timestamp = int(time.time())  # Getting the current timestamp
        self.db_name = f"{base_name}_{timestamp}.sqlite"  # Appending timestamp to ensure uniqueness
        self.conn = sqlite3.connect(self.db_name)
        self.df.to_sql(self.table_name, self.conn, if_exists='replace', index=False)

    def runsql(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()

        # Check if the query is a SELECT statement
        if query.strip().upper().startswith('SELECT'):
            result = pd.read_sql(query, self.conn)
            print(result)
            return result

    def show(self):
        # Display all data from the database
        return self.runsql(f'SELECT * FROM {self.table_name}')

    def kill(self):
        # Close the connection
        self.conn.close()
        # Remove the SQLite database file
        os.remove(self.db_name)

    def __del__(self):
        # Just to make sure connection is closed if not already
        if self.conn:
            self.conn.close()
