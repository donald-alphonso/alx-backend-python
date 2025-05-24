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

def transactional(func):
    """
    Decorator that manages database transactions

    This decorator is like a safety net that catches you if you fall.
    If everything goes well, it saves you changes. If something breaks,
    it undoes everything to keep your data safe.
    """

    @functools.wraps(func)
    def wrapper(con, *args, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Starting transaction...")

        try:
            # Begin transaction (SQLite uses autocomit=False by default)
            # Start making promises that we might need to keep or take back

            result = func(conn, *args, **kwargs)

            # Commit the transaction if everything went well
            # Keep all our promises because everything worked perfectly

            conn.commit()
            print(f"[{timestamp}] Transaction completed successfully")
            return result
        
        except Exception as e:
            # Rollback the transaction if something went wrong
            # Take back all our promises because something broke

            conn.rollback()
            print(f"[{timestamp}] Transaction rolled back due to error: {e}")
            raise

    return wrapper

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
cursor = conn.cursor() 
cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
#### Update user's email with automatic transaction handling 

update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')