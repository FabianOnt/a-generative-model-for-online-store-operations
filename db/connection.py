import mysql.connector
from config.db_config import DB_CONFIG

def get_connection():
    """
    Establish and return a MySQL connection using DB_CONFIG.
    """
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    return conn