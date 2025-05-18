#!/usr/bin/python3
import mysql.connector

def stream_user_ages():
    """
    Generator that yields one user age at a time from the user_data table.
    """
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ALX_prodev'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT age FROM user_data")
        for (age,) in cursor:
            yield age
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def compute_average_age():
    """
    Compute and print the average age using the stream_user_ages generator.
    """
    total = 0
    count = 0
    for age in stream_user_ages():
        total += age
        count += 1

    if count == 0:
        print("Average age of users: 0")
    else:
        average = total / count
        print(f"Average age of users: {average:.2f}")

if __name__ == "__main__":
    compute_average_age()
