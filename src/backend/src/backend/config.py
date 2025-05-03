import os

# Application settings
APP_NAME = os.getenv("APP_NAME", "DevOps Study Tracker")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "22112"))

# Data Storage Configuration
DATA_DIR = os.getenv(
    "DATA_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),
)


# CORS Configuration
# Environment variables for CORS lists should be provided as comma-separated values
# For example: CORS_ALLOW_ORIGINS=https://example.com,https://api.example.com
# Using "*" will be converted to ["*"] for wildcard access
def parse_list_env(env_name, default="*"):
    value = os.getenv(env_name, default)
    if value == "*":
        return ["*"]
    return [item.strip() for item in value.split(",")]


CORS_ALLOW_ORIGINS = parse_list_env("CORS_ALLOW_ORIGINS")
CORS_ALLOW_METHODS = parse_list_env("CORS_ALLOW_METHODS")
CORS_ALLOW_HEADERS = parse_list_env("CORS_ALLOW_HEADERS")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
