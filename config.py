import os

class Config:
    # MySQL database connection details
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "your_password")  # Update this
    MYSQL_DB = os.getenv("MYSQL_DB", "minishop")
    MYSQL_CURSORCLASS = 'DictCursor'  # So results will be in dict format
