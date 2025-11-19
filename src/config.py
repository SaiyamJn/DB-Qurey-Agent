import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_PRIORITY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
]

# Streamlit Configuration
PAGE_TITLE = "DataSense"
PAGE_LAYOUT = "wide"

# Database Configuration
SUPPORTED_SQL_DB_TYPES = ["PostgreSQL", "MySQL", "SQLite", "SQL Server"]
SUPPORTED_NOSQL_DB_TYPES = ["MongoDB", "Redis", "Cassandra"]
SUPPORTED_DB_TYPES = SUPPORTED_SQL_DB_TYPES + SUPPORTED_NOSQL_DB_TYPES
DEFAULT_DB_TYPE = "PostgreSQL"

# CSV Configuration
SUPPORTED_FILE_TYPES = ["csv"]
CSV_ENCODINGS = ["utf-8", "latin-1", "iso-8859-1"]

# UI Configuration
PREVIEW_ROWS_DEFAULT = 10
PREVIEW_ROWS_MIN = 5
PREVIEW_ROWS_MAX = 100