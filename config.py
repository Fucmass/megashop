import os

class Config:
    # MySQL database connection details
    MYSQL_HOST = os.getenv("MYSQL_HOST", "10.2.3.221")
    MYSQL_USER = os.getenv("MYSQL_USER", "Aron")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "pppppppppp")  # Default password
    MYSQL_DB = os.getenv("MYSQL_DB", "megashop")
    MYSQL_CURSORCLASS = 'DictCursor'  # So results will be in dict format

    # Debugging: Print the values (for testing purposes, but do not expose sensitive data in production)
    print(f"Using MySQL Host: {MYSQL_HOST} USER: {MYSQL_USER} PASSWORD {MYSQL_PASSWORD} Database: {MYSQL_DB}")