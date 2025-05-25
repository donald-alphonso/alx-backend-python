import asyncio
import aiosqlite
from datetime import datetime

async def async_fetch_users():
    """
    Asynchronously fetch all users from the database
    
    This is like a chef who can start preparing ingredients 
    while other dishes are cooking - no waiting around!
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Starting async_fetch_users...")
    
    try:
        # Open async database connection
        # Open a magic door that doesn't block other doors from opening
        async with aiosqlite.connect('users.db') as db:
            print(f"[{timestamp}] async_fetch_users: Database connected")
            
            # Execute the query asynchronously
            # Ask a question without stopping other conversations
            cursor = await db.execute("SELECT * FROM users")
            users = await cursor.fetchall()
            
            print(f"[{timestamp}] async_fetch_users: Found {len(users)} users")
            
            # Simulate some processing time
            # Pretend we're doing some work (like seasoning a dish)
            await asyncio.sleep(1)
            
            print(f"[{timestamp}] async_fetch_users: Completed")
            return users
            
    except Exception as e:
        print(f"[{timestamp}] Error in async_fetch_users: {e}")
        raise

async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database
    
    This is like another chef working on a different dish
    at the same time as the first chef!    
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Starting async_fetch_older_users...")
    
    try:
        # Open async database connection
        # Open another magic door that works independently
        async with aiosqlite.connect('users.db') as db:
            print(f"[{timestamp}] async_fetch_older_users: Database connected")
            
            # Execute the query asynchronously
            # Ask a different question at the same time
            cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
            older_users = await cursor.fetchall()
            
            print(f"[{timestamp}] async_fetch_older_users: Found {len(older_users)} users older than 40")
            
            # Simulate some processing time
            # Pretend we're doing different work (like chopping vegetables)
            await asyncio.sleep(1.5)
            
            print(f"[{timestamp}] async_fetch_older_users: Completed")
            return older_users
            
    except Exception as e:
        print(f"[{timestamp}] Error in async_fetch_older_users: {e}")
        raise

async def fetch_concurrently():
    """
    Execute both queries concurrently using asyncio.gather
    
    This is like having two chefs work on different dishes
    at the same time, and then serving both dishes together!    
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Starting concurrent fetch operations...")
    
    try:
        # Execute both functions concurrently
        # Start both chefs cooking at the same time
        start_time = asyncio.get_event_loop().time()
        
        # Use asyncio.gather to run both queries concurrently
        # Tell both chefs to start cooking and wait for both to finish
        all_users, older_users = await asyncio.gather(
            async_fetch_users(),
            async_fetch_older_users()
        )
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        
        print(f"\n[{timestamp}] ===== CONCURRENT RESULTS =====")
        print(f"[{timestamp}] Total execution time: {total_time:.2f} seconds")
        print(f"[{timestamp}] Both queries completed concurrently!")
        
        # Display results from first query
        # Show what the first chef cooked
        print(f"\n[{timestamp}] === ALL USERS (from async_fetch_users) ===")
        for user in all_users:
            print(f"  ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, Email: {user[3]}")
        
        # Display results from second query
        # Show what the second chef cooked
        print(f"\n[{timestamp}] === USERS OLDER THAN 40 (from async_fetch_older_users) ===")
        for user in older_users:
            print(f"  ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, Email: {user[3]}")
        
        print(f"\n[{timestamp}] Concurrent execution completed successfully!")
        
        return all_users, older_users
        
    except Exception as e:
        print(f"[{timestamp}] Error in fetch_concurrently: {e}")
        raise

def main():
    """
    Main function to run the concurrent async operations
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Starting Concurrent Asynchronous Database Operations Demo")
    print(f"[{timestamp}] " + "="*60)
    
    # Run the async operations
    # Start our kitchen with two chefs working together!
    asyncio.run(async_main())

async def async_main():
    """
    Async main function to coordinate all operations
    """
    try:
        
        # Run concurrent operations
        # Now let both chefs start cooking!
        await fetch_concurrently()
        
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Error in main execution: {e}")

if __name__ == "__main__":
    main()