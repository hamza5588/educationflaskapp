# # app.py
# from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
# from functools import wraps
# import sqlite3
# import hashlib
# from datetime import datetime
# from langchain_google_genai import ChatGoogleGenerativeAI

# app = Flask(__name__)
# app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

# # Database functions
# def init_db():
#     conn = sqlite3.connect('users.db')
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             name TEXT,
#             email TEXT PRIMARY KEY,
#             password TEXT,
#             api_key TEXT,
#             grade TEXT,
#             school TEXT,
#             medium TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()


# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# def save_user(name, email, password, api_key, grade, school, medium):
#     conn = sqlite3.connect('users.db')
#     c = conn.cursor()
#     try:
#         c.execute(
#             "INSERT INTO users (name, email, password, api_key, grade, school, medium) VALUES (?, ?, ?, ?, ?, ?, ?)",
#             (name, email, hash_password(password), api_key, grade, school, medium)
#         )
#         conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         return False
#     finally:
#         conn.close()



# def get_user(email, password):
#     conn = sqlite3.connect('users.db')
#     c = conn.cursor()
#     c.execute(
#         "SELECT * FROM users WHERE email=? AND password=?",
#         (email, hash_password(password))
#     )
#     user = c.fetchone()
#     conn.close()
#     return user


# def update_api_key(email, new_api_key):
#     conn = sqlite3.connect('users.db')
#     c = conn.cursor()
#     c.execute(
#         "UPDATE users SET api_key=? WHERE email=?",
#         (new_api_key, email)
#     )
#     conn.commit()
#     conn.close()

# # Login decorator
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user' not in session:
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function

# # Routes
# @app.route('/')
# def index():
#     if 'user' in session:
#         return redirect(url_for('chat'))
#     return redirect(url_for('login'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
        
#         user = get_user(email, password)
#         if user:
#             session['user'] = {
#                 'name': user[0],
#                 'email': user[1],
#                 'api_key': user[3],
#                 'grade': user[4],
#                 'school': user[5],
#                 'medium': user[6]
#             }
#             flash('Welcome back!', 'success')
#             return redirect(url_for('chat'))
#         flash('Invalid credentials!', 'error')
#     return render_template('login.html')


# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         password = request.form['password']
#         api_key = request.form['api_key']
#         grade = request.form['grade']
#         school = request.form['school']
#         medium = request.form['medium']
        
#         if save_user(name, email, password, api_key, grade, school, medium):
#             flash('Account created successfully!', 'success')
#             return redirect(url_for('login'))
#         flash('Email already exists!', 'error')
#     return render_template('signup.html')


# @app.route('/chat')
# @login_required
# def chat():
#     return render_template('chat.html', user=session['user'])

# @app.route('/send_message', methods=['POST'])
# @login_required
# def send_message():
#     data = request.json
#     user_message = data.get('message')
    
#     if user_message:
#         llm = ChatGoogleGenerativeAI(
#             model="gemini-1.5-pro",
#             google_api_key=session['user']['api_key'],
#             temperature=0.1,
#             max_tokens=150,
#             timeout=10,
#             max_retries=1
#         )
        
#         user_context = {
#             "name": session['user']['name'],
#             "grade": session['user'].get('grade'),
#             "school": session['user'].get('school'),
#             "medium": session['user'].get('medium')
#         }
        
#         full_message = f"Context: {user_context}\nMessage: {user_message}"
        
#         try:
#             response = llm.invoke(full_message)
#             return jsonify({
#                 'status': 'success',
#                 'response': response.content
#             })
#         except Exception as e:
#             return jsonify({
#                 'status': 'error',
#                 'message': str(e)
#             })
    
#     return jsonify({
#         'status': 'error',
#         'message': 'No message provided'
#     })


# @app.route('/update_api_key', methods=['POST'])
# @login_required
# def update_api_key_route():
#     new_api_key = request.form['api_key']
#     if new_api_key:
#         update_api_key(session['user']['email'], new_api_key)
#         session['user']['api_key'] = new_api_key
#         flash('API Key updated successfully!', 'success')
#     return redirect(url_for('chat'))

# @app.route('/logout')
# def logout():
#     session.pop('user', None)
#     return redirect(url_for('login'))

# if __name__ == '__main__':
#     init_db()
#     app.run(debug=True)


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
            api_key TEXT,
            grade TEXT,
            school TEXT,
            medium TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            message TEXT,
            response TEXT,
            validation TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(name, email, password, api_key, grade, school, medium):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (name, email, password, api_key, grade, school, medium) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, hash_password(password), api_key, grade, school, medium)
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

def save_chat_history(user_email, message, response, validation=None):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO chat_history (user_email, message, response, validation, timestamp) VALUES (?, ?, ?, ?, datetime('now'))",
        (user_email, message, response, validation)
    )
    conn.commit()
    conn.close()

def validate_with_ai(user_message, generated_response):
    checker_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key="your_google_api_key_for_checker",
        temperature=0.1,
        max_tokens=150,
        timeout=10,
        max_retries=1
    )

    validation_prompt = (
        f"Validate the following response for accuracy and relevance.\n"
        f"User Message: {user_message}\n"
        f"Generated Response: {generated_response}\n"
        f"Does the response accurately and relevantly address the user's message? "
        f"Respond with 'Yes' or 'No', and explain why."
    )
    
    try:
        validation_response = checker_llm.invoke(validation_prompt)
        return validation_response.content
    except Exception as e:
        return f"Validation Error: {e}"

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
                'api_key': user[3],
                'grade': user[4],
                'school': user[5],
                'medium': user[6]
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
        grade = request.form['grade']
        school = request.form['school']
        medium = request.form['medium']
        
        if save_user(name, email, password, api_key, grade, school, medium):
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
            temperature=0.5,  # Adjust temperature for more human-like randomness
            max_tokens=150,
            timeout=10,
            max_retries=1
        )
        
        user_context = {
            "name": session['user']['name'],
            "grade": session['user'].get('grade'),
            "medium": session['user'].get('medium'),
            "school": session['user'].get('school')
        }

        # Include context in the prompt
        full_message = (
            f"You are an AI assistant for students. Your goal is to be conversational and friendly.\n"
            f"Student Name: {user_context['name']}\n"
            f"Grade: {user_context['grade']}\n"
            f"Medium: {user_context['medium']}\n"
            f"School: {user_context['school']}\n"
            f"Message from {user_context['name']}: {user_message}\n"
            f"Respond like a friendly and knowledgeable assistant."
        )

        try:
            response = llm.invoke(full_message)
            generated_response = response.content

            # Validate the response using the Checker Agent
            validation_result = validate_with_ai(user_message, generated_response)

            # Save conversation and validation result to the database
            save_chat_history(session['user']['email'], user_message, generated_response, validation_result)

            return jsonify({
                'status': 'success',
                'response': generated_response,
                'validation': validation_result
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


@app.route('/history', methods=['GET'])
@login_required
def get_history():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT message, response, validation, timestamp FROM chat_history WHERE user_email=? ORDER BY timestamp DESC", 
              (session['user']['email'],))
    history = c.fetchall()
    conn.close()
    return jsonify(history)

@app.route('/update_api_key', methods=['POST'])
@login_required
def update_api_key_route():
    new_api_key = request.form['api_key']
    if new_api_key:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("UPDATE users SET api_key=? WHERE email=?", (new_api_key, session['user']['email']))
        conn.commit()
        conn.close()
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
