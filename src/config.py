import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_FOLDER= os.path.join(DATA_DIR, 'uploads')
DB_PATH = os.path.join(DATA_DIR, 'warehouse.db')  # Renamed for clarity
METADATA_OUTPUT_PATH = os.path.join(DATA_DIR, 'metadata_output.json')
SUPPORTED_EXTENSIONS= {'.csv', '.json', '.xlsx', '.xls'}

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("BASE_DIR:", BASE_DIR)
print("DATA_DIR:", DATA_DIR)
print("UPLOAD_FOLDER:", UPLOAD_FOLDER)
