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

def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries database operations on failure
    
    This decorator is like a determined child who keeps asking
    "Can we try again?" until they get what they want or run out of chances.
    
    Args:
        retries (int): Number of retry attempsts (default: 3)
        delay (int): Delay in seconds between retries (default : 2)
    """
    def decorator(fun):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Try the function multiple times
            # Keep trying like a persistent child
            
            for attempt in range(retries +1):
                try:
                    if attempt > 0
                        print(f"[{timestamp}] Retry attempt {attempt}/{retries}")
                        
                    result = func(*args, **kwargs)
                    
                    if attempt > 0:
                        print(f"[{timestamp}] Operation succeeded on retry {attempt}")
                        
                    return result
                
                except Exception as e:
                    print(f"[{timestamp}] Attempt {attempt + 1} failed: {e}")
                    
                    # If this was our last attempt, give up
                    # If we've tried all our chances, it's time to give up
                    
                    if attempt == retries:
                        print(f"[{timestamp}] All {retries + 1} attempts failed. Giving up.")
                        raise
                    
                    # Wait before trying again
                    # Take a little break before trying again
                    print(f"[{timestamp}] Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    
        return wrapper
    
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)

def fetch_users_with_retry(conn):
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)