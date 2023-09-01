import os
import mysql.connector
import traceback
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv('DB_HOST')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
PORT = os.getenv('DB_PORT')
DATABASE = os.getenv('DATABASE')

def connect_database():
    try:
        db_conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, port=PORT, database=DATABASE)
        db_cursor = db_conn.cursor(dictionary=True)
        return db_conn, db_cursor
    except:
        traceback.print_exc()
        return False, False
