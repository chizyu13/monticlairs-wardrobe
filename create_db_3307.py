import MySQLdb

# Connect to MySQL on port 3307 without specifying a database
try:
    connection = MySQLdb.connect(
        host='localhost',
        user='root',
        password='',
        port=3307
    )
    
    cursor = connection.cursor()
    
    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS montclair_wardrobe")
    print("✓ Database 'montclair_wardrobe' created successfully on port 3307")
    
    # Show databases to confirm
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    print("\nAvailable databases on port 3307:")
    for db in databases:
        print(f"  - {db[0]}")
    
    cursor.close()
    connection.close()
    
except MySQLdb.Error as e:
    print(f"Error: {e}")
    print("\nMake sure MySQL is running on port 3307 in XAMPP")
