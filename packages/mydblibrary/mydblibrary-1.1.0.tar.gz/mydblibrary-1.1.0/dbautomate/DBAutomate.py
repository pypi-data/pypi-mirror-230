import sys
import psycopg2
import warnings
from psycopg2 import OperationalError
from dbautomate.config_file import *

warnings.filterwarnings("ignore")


# Connecting to Postgresql
def connect_to_database():
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=dbname,
            user=user,
            password=passwd
        )
        print("Connection established successfully")
        return conn
    except OperationalError as e:
        print(f"An error occurred while connecting to the PostgresSQL database: {e}")
        sys.exit(str(e))
        return None


# Executing the Query where it fetches the data from table.
def execute_query(query):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result
