import sqlite3 
import functools
from datetime import datetime

def with_db_connection(func):
    """
    Decorator that automatically handles database connections
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Opening database connection...")
        
        conn = sqlite3.connect('users.db')
        
        try:
            result = func(conn, *args, **kwargs)
            print(f"[{timestamp}] Database operation completed successfully")
            return result
            
        except Exception as e:
            print(f"[{timestamp}] Error during database operation: {e}")
            raise
            
        finally:
            conn.close()
            print(f"[{timestamp}] Database connection closed")
    
    return wrapper

# Global cache dictionary - our memory notebook
# English: This is our magic notebook that remembers everything
# Français: C'est notre carnet magique qui se souvient de tout
query_cache = {}

def cache_query(func):
    """
    Decorator that caches query results to avoid redundant database calls
    
    English: This decorator is like having a super memory that never forgets.
    It remembers every question and answer so you don't have to ask twice!
    
    Français: Ce décorateur est comme avoir une super mémoire qui n'oublie jamais.
    Il se souvient de chaque question et réponse pour que tu n'aies pas à demander deux fois !
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a cache key from the query
        # English: Make a unique name for this question so we can find it later
        # Français: Créer un nom unique pour cette question pour qu'on puisse la retrouver plus tard
        
        # Get the query from arguments
        query = None
        if 'query' in kwargs:
            query = kwargs['query']
        elif args:
            # Assuming query is the first argument after conn
            query = args[0] if len(args) > 0 else None
        
        if query is None:
            # If we can't find a query, just execute without caching
            print(f"[{timestamp}] No query found for caching, executing directly")
            return func(conn, *args, **kwargs)
        
        # Use the query as the cache key
        cache_key = query.strip().lower()  # Normalize the query
        
        # Check if we already have this answer in our notebook
        # English: Look in our memory notebook to see if we already know the answer
        # Français: Regarder dans notre carnet de mémoire pour voir si on connaît déjà la réponse
        if cache_key in query_cache:
            print(f"[{timestamp}] Cache HIT! Returning cached result for query: {query}")
            print(f"[{timestamp}] Cached at: {query_cache[cache_key]['timestamp']}")
            return query_cache[cache_key]['result']
        
        # If we don't have the answer, do the work and remember it
        # English: If we don't know the answer, do the hard work and write it down
        # Français: Si on ne connaît pas la réponse, faire le travail difficile et l'écrire
        print(f"[{timestamp}] Cache MISS! Executing query: {query}")
        result = func(conn, *args, **kwargs)
        
        # Store the result in our cache notebook
        # English: Write down the question and answer in our memory notebook
        # Français: Écrire la question et la réponse dans notre carnet de mémoire
        query_cache[cache_key] = {
            'result': result,
            'timestamp': timestamp,
            'query': query
        }
        
        print(f"[{timestamp}] Result cached for future use")
        return result
    
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")