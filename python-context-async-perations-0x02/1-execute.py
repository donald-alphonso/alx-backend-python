import sqlite3
from datetime import datetime

class ExecuteQuery:
    """
    Reusable context manager that executes queries with automatic connection handling
    
    This is like having a personal assistant who not only opens doors,
    but also knows exactly what question to ask and gets the answer for you!
    
    mais sait aussi exactement quelle question poser et obtient la réponse pour toi !
    """
    
    def __init__(self, query, parameters=None, db_name='users.db'):
        """
        Initialize the query context manager
        
        Tell our smart assistant what question to ask and any extra details
        
        Args:
            query (str): SQL query to execute
            parameters (tuple): Parameters for the query (optional)
            db_name (str): Database file name
        """
        self.query = query
        self.parameters = parameters or ()
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.results = None
        
    def __enter__(self):
        """
        Enter the context - open connection and execute query
        
        Our assistant opens the door, asks the question, and gets ready to give you the answer
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Opening database connection and preparing query...")
        
        try:
            # Open database connection
            # Open the magic door to the database
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            
            print(f"[{timestamp}] Executing query: {self.query}")
            if self.parameters:
                print(f"[{timestamp}] With parameters: {self.parameters}")
            
            # Execute the query
            # Ask the database the question
            if self.parameters:
                self.cursor.execute(self.query, self.parameters)
            else:
                self.cursor.execute(self.query)
            
            # Fetch the results
            # Get the answer from the database
            self.results = self.cursor.fetchall()
            
            print(f"[{timestamp}] Query executed successfully! Found {len(self.results)} results")
            
            # Return the results so they can be used
            # Hand you the answer
            return self.results
            
        except Exception as e:
            print(f"[{timestamp}] Error executing query: {e}")
            # Clean up if something went wrong
            if self.connection:
                self.connection.close()
            raise
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context - close connection and clean up
        
        Our assistant cleans up everything and locks the door, 
        no matter what happened
        
        peu importe ce qui s'est passé
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Close cursor and connection
        # Put away all the tools and lock the door
        if self.cursor:
            self.cursor.close()
            
        if self.connection:
            try:
                self.connection.close()
                print(f"[{timestamp}] Database connection closed successfully")
            except Exception as e:
                print(f"[{timestamp}] Error closing database connection: {e}")
        
        # Handle any exceptions
        # Report any problems that happened
        if exc_type is not None:
            print(f"[{timestamp}] Exception occurred: {exc_type.__name__}: {exc_value}")
            return False
        
        return True

def main():
    """
    Main function to demonstrate the ExecuteQuery context manager
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] Demonstrating ExecuteQuery context manager...")
    
    # Example 1: Query for users older than 25
    # Let our smart assistant ask for users older than 25
    print(f"\n[{timestamp}] === Example 1: Users older than 25 ===")
    try:
        with ExecuteQuery("SELECT * FROM users WHERE age > ?", (25,)) as results:
            print(f"[{timestamp}] Results received in context:")
            for user in results:
                print(f"  User ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, Email: {user[3]}")
                
    except Exception as e:
        print(f"[{timestamp}] Error in example 1: {e}")
    
    # Example 2: Query for all users
    # Let our assistant get all users
    print(f"\n[{timestamp}] === Example 2: All users ===")
    try:
        with ExecuteQuery("SELECT * FROM users") as results:
            print(f"[{timestamp}] Found {len(results)} total users:")
            for user in results:
                print(f"  {user[1]} (Age: {user[2]})")
                
    except Exception as e:
        print(f"[{timestamp}] Error in example 2: {e}")
    
    # Example 3: Query with specific age requirement (as in task description)
    # Ask for users older than 25 as specified in the task
    print(f"\n[{timestamp}] === Example 3: Task Specific Query - Users older than 25 ===")
    try:
        with ExecuteQuery("SELECT * FROM users WHERE age > ?", (25,)) as results:
            print(f"[{timestamp}] Task query executed successfully!")
            print(f"[{timestamp}] Users older than 25:")
            for user in results:
                print(f"  ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, Email: {user[3]}")
                
    except Exception as e:
        print(f"[{timestamp}] Error in task specific query: {e}")

if __name__ == "__main__":
    main()