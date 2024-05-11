import mysql.connector
from mysql.connector import Error
from flask import Flask


app = Flask(__name__)
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='Camael26Macarthur',
            database='Recover_me'
        )
        app.logger.info("Connection to MySQL DB successful")
        return connection
    except mysql.connector.Error as e:
        app.logger.error(f"Connection error: {e}")
        return None

