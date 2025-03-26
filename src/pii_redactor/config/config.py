import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Data paths
DATA_PATH = os.path.join(DATA_DIR, "pii_data.json")

# Model paths
MODEL_PATH = os.path.join(MODELS_DIR, "pii_model")
MODEL_CONFIG_PATH = os.path.join(MODELS_DIR, "config.cfg")

# PII Categories
PII_CATEGORIES = ["NAME", "ORGANIZATION", "ADDRESS", "EMAIL", "PHONE_NUMBER"]

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "PII Redactor API"
API_DESCRIPTION = (
    "An API to redact Personally Identifiable Information (PII) from text."
)
API_VERSION = "1.0.0"

# Logging Configuration
LOG_LEVEL = "INFO"
