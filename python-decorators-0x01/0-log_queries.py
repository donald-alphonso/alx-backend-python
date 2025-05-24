import sqlite3
import functools

#### decorator to log SQL queries

def log_queries(func):
    """
    Decorator that logs SQL queries before execution
    this decorator acts like a spy taht watches and reports what SQL
    queries are being executed by any function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extraact the query from function arguments
        # We look for the 'query' in the function's inputs

        # Check if 'query' is in keyword arguments
        if 'query' in kwargs:
            query = kwargs['query']
        # Check if 'query' is in positional arguments (assuming it's the first one)
        elif args and len(args) > 0:
            # For this specific case, we know query is passed as first argument
            query = args[0] if isinstance(args[0], str) else None
        else:
            query = "Unknown query"

        # Log the query
        # Write down what SQL command we're about to run
        print(f"Executing query: {query}")

        # Call the original function
        return func(*args, **kwargs)

    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")