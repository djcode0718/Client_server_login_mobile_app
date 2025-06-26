from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # 🔓 Allow cross-origin requests from Flutter

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

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

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

    if user:
        print(f"correct {username}: {password}")
        return jsonify({'status': 'success', 'message': 'Login successful'})
    
    else:
        print(f"wrong {username}: {password}")
        return jsonify({'status': 'fail', 'message': 'Invalid credentials'})

@app.route('/signup', methods=['POST'])
def signup():
    username = get_data(request, 'username')
    password = get_data(request, 'password')

    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        return jsonify({'status': 'success', 'message': 'Signup successful'})
    except sqlite3.IntegrityError:
        return jsonify({'status': 'fail', 'message': 'Username already exists'})

if __name__ == '__main__':
    print("✅ Starting Flask server...")
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
