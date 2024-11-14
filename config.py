import os

class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "10.2.3.221")
    MYSQL_USER = os.getenv("MYSQL_USER", "Aron")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "pppppppppp")
    MYSQL_DB = os.getenv("MYSQL_DB", "megashop")
    MYSQL_PORT = 3306


    # Print for debugging (excluding sensitive data)
    print(f"Using MySQL Host: {MYSQL_HOST}, Database: {MYSQL_DB}")

# Example usage for connection (with PyMySQL or mysql-connector-python)
import pymysql  # or import mysql.connector