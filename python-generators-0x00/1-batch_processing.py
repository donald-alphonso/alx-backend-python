import mysql.connector

def stream_users_in_batches(batch_size=25):
    con = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',j
            database='ALX_prodev'
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:    
            conn.close()

def batch_processing(batch_size=25):
    try:
        for batch in stream_users_in_batches(batch_size):
            for user in batch:
                if user['age'] > 25:
                    print(user)
    except Exception as e:
        print(f"Error during batch processing: {e}")
