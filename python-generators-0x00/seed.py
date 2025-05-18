import mysql.connector
import csv
import uuid

def connect_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            usesr='root',
            password=''
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        connection.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")

def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root'
            password='',
            database='ALX_prodev'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def create_table(connection):
    try:
        cursor = connection.cursor()
        create_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL
        )
        """
        cursor.execute(create_query)
        connection.commit()
        print("Table user_data created successfully.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")

def insert_data(connection, csv_file):
    try:
        cursor = connection.cursor()
        With open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                cursor.execute("SELECT * FROM user_data WHERE email = %s", (row['email'],))
                if cursor.fetchone():
                    continue
                # Insert new user
                insert_query = "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)"
                uid = str(uuid.uuid4())
                cursor.execute(insert_query, (uid, row['name'], row['email'], row['age']))
        connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error inserting data: {e}")
