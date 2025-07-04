import sqlite3
from datetime import datetime

class DatabaseConnection:
    """
    Custom class-based context manager for database connections.

    This class is like a smart doorkeeper that automatically opens the database door
    when you enter and closes it when you leave, no matter what happens inside.
    """

    def __init__(self, db_name='user.db'):
        """
        Initialize the context manager with the database name.

        Set up our smart doorkeeper with the name of the database.
        """

        self.db_name = db_name
        self.connection = None

    def __enter__(self):
        """
        Open the database connection when entering the context.
        This is like unlocking the door to the database.
        """

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Opening database connection to {self.db_name}")

        try:
            self.connection = sqlite3.connect(self.db_name)
            print(f"[{timestamp}] Database connection established successfully")

            return self.connection
        except Exception as e:
            print(f"[{timestamp}] Failed to open database connection: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close the database connection when exiting the context.
        This is like locking the door to the database.
        """

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.connection:
            try:
                self.connection.close()
                print(f"[{timestamp}] Database connection closed successfully")
            except Exception as e:
                print(f"[{timestamp}] Failed to close database connection: {e}")
        else:
            print(f"[{timestamp}] No database connection to close")
        
        return False

    def main():
        """
        Main function to demonstrate the context manager
        """
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Demonstrating DatabaseConnection context manager...")
        
        # Use the context manager with the 'with' statement
        # Use our smart doorkeeper to safely visit the database
        try:
            with DatabaseConnection('users.db') as conn:
                print(f"[{timestamp}] Inside the context - connection is active")
                
                # Perform the query
                # Ask the database our question
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
                results = cursor.fetchall()
                
                print(f"[{timestamp}] Query executed successfully!")
                print(f"[{timestamp}] Found {len(results)} users:")
                
                # Print the results
                # Show what the database told us
                for user in results:
                    print(f"  User ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, Email: {user[3]}")
                    
            print(f"[{timestamp}] Exited the context - connection automatically closed")
            
        except Exception as e:
            print(f"[{timestamp}] An error occurred: {e}")