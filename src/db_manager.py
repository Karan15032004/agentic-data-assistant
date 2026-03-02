import pandas as pd
import re
from sqlalchemy import create_engine, inspect
from src.config import DB_PATH

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(f"sqlite:///{DB_PATH}") #“Create a connection interface to the SQLite database located at DB_PATH.”

    def _sanitize_table_name(self, name: str) -> str:
        clean_name = name.lower() #table names are all lower
        clean_name = re.sub(r'\W+', '_', clean_name) #replace all non-alphanumeric with _
        return clean_name.strip('_') #remove all '_' from start and end

    def table_exists(self, table_name: str) -> bool:
        clean_name = self._sanitize_table_name(table_name) #class ke current object pe hi picchla function call kar raha
        inspector = inspect(self.engine)
        return clean_name in inspector.get_table_names()

    def create_table(self, df: pd.DataFrame, raw_table_name: str, replace: bool = False):
        """
        Returns: (success: bool, message: str, final_table_name: str)
        """
        try:
            # 1. Sanitize
            table_name = self._sanitize_table_name(raw_table_name)

            # 2. Logic
            if self.table_exists(table_name):
                if replace:
                    action = 'replace'
                    msg = f"Table '{table_name}' exists. Overwriting."
                else:
                    action = 'append'
                    msg = f"Table '{table_name}' exists. Appending."
            else:
                action = 'replace'
                msg = f"Creating new table '{table_name}'."

            # 3. Execute
            df.to_sql(
                table_name,
                self.engine,
                if_exists=action,
                index=False,
                chunksize=1000
            )
            # RETURN THE ACTUAL TABLE NAME HERE
            return True, msg, table_name

        except Exception as e:
            return False, f"Database Error: {str(e)}", None

    def get_table_sample(self, raw_table_name: str, limit=5):
        try:
            table_name = self._sanitize_table_name(raw_table_name)
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            return pd.read_sql(query, self.engine) #sends the query to database,SQLite executes it,returns the result and pandas converts it to a dataframe
        except Exception:
            return None
        
        
 # Clean Final Summary
#db_manager.py is responsible for:

#Sanitizing table names
#Checking if tables exist
#Deciding overwrite vs append
#Writing DataFrames into SQLite
#Returning operation status
#Providing a method to fetch sample data
#It is the database layer of your system.

