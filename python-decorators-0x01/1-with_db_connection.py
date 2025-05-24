import sqlite3
import functools
from datetime import datetime

def with_db_connection(func):
    """
    Decorator that automatically handles database connections
    
    This decorator is like a helpful doorman that opens and closes
    the database door for you automatically.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Log the connection attempt with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Opening database connection...")

        # Open the database connection
        # Open the magic door to talk to the database
        conn = sqlite3.connect('users.db')

        try:
            # Call the original function with the connection
            # Do the work with the open door
            result = func(conn, *args, **kwargs)

            print(f"[{timestamp}] Database operation completed successfully")
            return result

        except Exception as e:
            print(f"[{timestamp}] Error during database operation: {e}")
            raise

        finally:
            conn.close()
            print(f"[{timestamp}] Closing database connection...")

    return wrapper

@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone()

#### Fetch user by ID with automatic connection handling 

user = get_user_by_id(user_id=1)
print(user)