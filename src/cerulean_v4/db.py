import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='users',
        unix_socket='/data/mysql.sock'
    )

def create_user(username, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255))')
    cursor.execute('SELECT username FROM users WHERE username=%s', (username,))
    if cursor.fetchone():
        db.close()
        return False
    hashed = generate_password_hash(password)
    cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed))
    db.commit()
    db.close()
    return True

def validate_user(username, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT password FROM users WHERE username=%s', (username,))
    row = cursor.fetchone()
    db.close()
    if row and check_password_hash(row[0], password):
        return True
    return False
