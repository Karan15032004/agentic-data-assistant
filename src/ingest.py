import os
import pandas as pd
import re
from src.config import UPLOAD_FOLDER,SUPPORTED_EXTENSIONS
from src.db_manager import DatabaseManager

class IngestionEngine:
    def __init__(self):
        self.db = DatabaseManager()

    def process_file(self, filename: str) -> dict:
        """
        Orchestrates the ingestion: Load -> Clean -> Store -> Report.
        """
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Check the File
        if not os.path.exists(file_path):
             return {"status": "failed", "error": f"File not found: {filename}"}
        
        ext = os.path.splitext(filename)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return {"status": "failed", "error": f"Unsupported extension: {ext}"}

        try:
            # Load the File
            df = self._load_file(file_path, ext)
            raw_count = len(df)

            # Clean It (Universal Only)
            df, duplicates_removed = self._clean_data(df)
            
            # Generate Table Name Candidate
            table_name_candidate = os.path.splitext(filename)[0] #superstore.csv becomes superstore
            
            success, msg, final_table_name = self.db.create_table(df, table_name_candidate, replace=True)

            if not success:
                return {"status": "failed", "error": msg}

            # Return a Summary Report
            return {
                "status": "success",
                "file_name": filename,
                "table_name": final_table_name, # Using the Real Name
                "rows_read": raw_count,
                "duplicates_removed": duplicates_removed,
                "rows_written": len(df),
                "columns_detected": len(df.columns),
                "column_names": list(df.columns),
                "message": msg
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _load_file(self, path, ext):
        """Standardized Loader."""
        if ext == '.csv':
            return pd.read_csv(path, low_memory=False)
        elif ext == '.json':
            return pd.read_json(path)
        elif ext in ['.xls', '.xlsx']:
            return pd.read_excel(path)
        

        raise ValueError(f"Unsupported file type inside loader: {ext}")

    def _clean_data(self, df):
        """
        Pure Cleaning: Headers, Whitespace, Duplicates.
        """
        # Normalize Column Names
        df.columns = [
            re.sub(r'\W+', '_', c.strip().lower()).strip('_') 
            for c in df.columns
        ]
        obj_cols = df.select_dtypes(include=['object']).columns
        for col in obj_cols:
            df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

        # Remove Exact Duplicates
        old_len = len(df)
        df = df.drop_duplicates()
        duplicates_removed = old_len - len(df)

        return df, duplicates_removed