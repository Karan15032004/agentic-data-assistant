import sys
import os
from src.ingest import IngestionEngine

def main():
    print(" Agentic Data System - Phase 1: Ingestion")
    print("==========================================")

    # 1. Get the filename from the command line (or default to 'train.csv')
    # Usage: python run_pipeline.py superstore.xlsx
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        target_file = 'train.csv'

    # 2. Check if file exists in uploads before running logic
    # (Just a quick user-friendly check before the engine starts)
    # We import UPLOAD_FOLDER here just for this print statement
    from src.config import UPLOAD_FOLDER
    file_path = os.path.join(UPLOAD_FOLDER, target_file)
    
    if not os.path.exists(file_path):
        print(f" Error: File '{target_file}' not found in 'data/uploads/'")
        print(f"   -> Please move your file to: {UPLOAD_FOLDER}")
        return

    engine = IngestionEngine()


    print(f"🚀 Starting Pipeline for: {target_file}...")
    
    # Run the Factory
    report = engine.process_file(target_file)

    # Print the Report
    print("\n" + "="*40)
    if report["status"] == "success":
        print(f" INGESTION SUCCESS")
        print(f"    File Name:    {report['file_name']}")
        print(f"    Table Name:   {report['table_name']}")
        print(f"    Rows Read:    {report['rows_read']}")
        print(f"    Duplicates:   {report['duplicates_removed']}")
        print(f"    Rows Written: {report['rows_written']}")
        print(f"    Columns:      {report['columns_detected']}")
    else:
        print(f" INGESTION FAILED")
        print(f"   ⚠️  Reason: {report.get('error')}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()