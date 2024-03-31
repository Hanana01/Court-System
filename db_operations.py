import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

cursor = db.cursor()

# Create database if not exists
cursor.execute("CREATE DATABASE IF NOT EXISTS userdb")
cursor.execute("USE userdb")

# Create users table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        username VARCHAR(255),
        email VARCHAR(255),
        phone VARCHAR(20),
        password VARCHAR(255),
        gender VARCHAR(20),
        status VARCHAR(255)
    )
""")
db.commit()
