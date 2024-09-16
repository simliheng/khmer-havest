import pymysql

# Replace these with your actual connection details
host = 'localhost'
port = 3307
user = 'root'
password = 'hawaii2005'
database = 'new_database'

try:
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
    if conn:
        print("Connection successful!")
except pymysql.MySQLError as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
