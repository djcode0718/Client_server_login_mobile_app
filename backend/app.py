from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

from argon2 import PasswordHasher

app = Flask(__name__)
CORS(app, supports_credentials=True)

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# Use Argon2id by default
ph = PasswordHasher()

# DB setup
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# Helper to extract from JSON or form
def get_data(req, key):
    return req.json.get(key) if req.is_json else req.form.get(key)

@app.route('/')
def home():
    return jsonify({"message": "API is running"})

@app.route('/login', methods=['POST'])
def login():
    username = get_data(request, 'username')
    password = get_data(request, 'password')

    if not username or not password:
        return jsonify({'status': 'fail', 'message': 'Missing username or password'})

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        row = c.fetchone()

    if not row:
        return jsonify({'status': 'fail', 'message': 'Invalid credentials'})

    stored_hash = row[0]

    try:
        ph.verify(stored_hash, password)
        # If verify passes, the password is correct
        print(f"✅ Correct credentials: {username}")
        return jsonify({'status': 'success', 'message': 'Login successful'})
    except Exception:
        print(f"❌ Wrong credentials: {username}")
        return jsonify({'status': 'fail', 'message': 'Invalid credentials'})

@app.route('/signup', methods=['POST'])
def signup():
    username = get_data(request, 'username')
    password = get_data(request, 'password')

    if not username or not password:
        return jsonify({'status': 'fail', 'message': 'Missing username or password'})

    try:
        hashed_password = ph.hash(password)

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()

        print(f"✅ User created: {username}")
        return jsonify({'status': 'success', 'message': 'Signup successful'})
    except sqlite3.IntegrityError:
        return jsonify({'status': 'fail', 'message': 'Username already exists'})

if __name__ == '__main__':
    print("✅ Starting Flask server...")
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
