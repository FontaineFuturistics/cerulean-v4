
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import configparser
import os

def get_db():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    config.read(config_path)
    db_cfg = config['database']
    db_path = db_cfg.get('db_path', os.path.join(os.path.dirname(__file__), 'data', 'users.db'))
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def create_user(username, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS mappings (username TEXT, urn TEXT, url TEXT, PRIMARY KEY (username, urn), FOREIGN KEY (username) REFERENCES users(username))')
    cursor.execute('SELECT username FROM users WHERE username=?', (username,))
    if cursor.fetchone():
        db.close()
        return False
    hashed = generate_password_hash(password)
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
    db.commit()
    db.close()
    return True
def get_mappings(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT urn, url FROM mappings WHERE username=?', (username,))
    mappings = cursor.fetchall()
    db.close()
    return dict(mappings)

def add_mapping(username, urn, url):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT OR REPLACE INTO mappings (username, urn, url) VALUES (?, ?, ?)', (username, urn, url))
    db.commit()
    db.close()

def remove_mapping(username, urn):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM mappings WHERE username=? AND urn=?', (username, urn))
    db.commit()
    db.close()

def validate_user(username, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT password FROM users WHERE username=?', (username,))
    row = cursor.fetchone()
    db.close()
    if row and check_password_hash(row[0], password):
        return True
    return False
