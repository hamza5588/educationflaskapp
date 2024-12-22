# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import sqlite3
import hashlib
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

# Database functions
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            name TEXT,
            email TEXT PRIMARY KEY,
            password TEXT,
            api_key TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(name, email, password, api_key):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (name, email, password, api_key) VALUES (?, ?, ?, ?)",
            (name, email, hash_password(password), api_key)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    )
    user = c.fetchone()
    conn.close()
    return user

def update_api_key(email, new_api_key):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(
        "UPDATE users SET api_key=? WHERE email=?",
        (new_api_key, email)
    )
    conn.commit()
    conn.close()

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = get_user(email, password)
        if user:
            session['user'] = {
                'name': user[0],
                'email': user[1],
                'api_key': user[3]
            }
            flash('Welcome back!', 'success')
            return redirect(url_for('chat'))
        flash('Invalid credentials!', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        api_key = request.form['api_key']
        
        if save_user(name, email, password, api_key):
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        flash('Email already exists!', 'error')
    return render_template('signup.html')

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=session['user'])

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    user_message = data.get('message')
    
    if user_message:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=session['user']['api_key'],
            temperature=0.1,
            max_tokens=150,
            timeout=10,
            max_retries=1
        )
        
        try:
            response = llm.invoke(user_message)
            return jsonify({
                'status': 'success',
                'response': response.content
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            })
    
    return jsonify({
        'status': 'error',
        'message': 'No message provided'
    })

@app.route('/update_api_key', methods=['POST'])
@login_required
def update_api_key_route():
    new_api_key = request.form['api_key']
    if new_api_key:
        update_api_key(session['user']['email'], new_api_key)
        session['user']['api_key'] = new_api_key
        flash('API Key updated successfully!', 'success')
    return redirect(url_for('chat'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)