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
import io
import os
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

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

# Speech-to-Text function
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Error with the speech recognition service; {e}")
        return ""

# Text-to-Speech function
def speak_text(text, filename="response.mp3"):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filename)
        playsound(filename)
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

# # Gemini Interaction
# def generate_response(user_message):
#     """Generates a response using the Gemini model."""
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-1.5-pro",
#         google_api_key=session['user']['api_key'],
#         temperature=0.5,
#         max_tokens=150,
#         timeout=10,
#         max_retries=1
#     )
    
#     try:
#         response = llm.invoke(user_message)
#         return response.content
#     except Exception as e:
#         print(f"Error generating response from Gemini: {e}")
#         return "I'm sorry, I encountered an error."
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

# @app.route('/send_message', methods=['POST'])
# @login_required
# def send_message():
#     data = request.json
#     user_message = data.get('message')
    
#     if user_message:
#         generated_response = generate_response(user_message)
#         validation_result = validate_with_ai(user_message, generated_response)
#         save_chat_history(session['user']['email'], user_message, generated_response, validation_result)

#         return jsonify({
#             'status': 'success',
#             'response': generated_response,
#             'validation': validation_result
#         })
    
#     return jsonify({
#         'status': 'error',
#         'message': 'No message provided'
#     })
# First, let's modify the generate_response function to handle prompt templates
def generate_response(user_message, prompt_template=None):
    """Generates a response using the Gemini model."""
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=session['user']['api_key'],
            temperature=0.7,
            max_tokens=150,
            timeout=10,
            max_retries=1
        )
        
        # Construct the full message
        if prompt_template and prompt_template.strip():
            full_message = f"{prompt_template.strip()}\n\nUser Input: {user_message}"
            print(f"Using prompt template: {full_message}")  # Debug log
        else:
            full_message = user_message
            print("No prompt template used")  # Debug log
        
        print(f"Sending message to Gemini: {full_message}")  # Debug log
        
        response = llm.invoke(full_message)
        return response.content
    except Exception as e:
        print(f"Error generating response from Gemini: {e}")  # Debug log
        return f"I'm sorry, I encountered an error: {str(e)}"

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    try:
        data = request.json
        user_message = data.get('message')
        prompt_template = data.get('promptTemplate')
        
        print(f"Received message: {user_message}")  # Debug log
        print(f"Received prompt template: {prompt_template}")  # Debug log

        if not user_message:
            return jsonify({'status': 'error', 'message': 'No message provided'})

        # Generate response with the prompt template
        generated_response = generate_response(user_message, prompt_template)
        print(f"Generated response: {generated_response}")  # Debug log
        
        # Save chat history
        save_chat_history(session['user']['email'], user_message, generated_response)

        # Generate audio response
        audio_filename = f"response_{session['user']['email']}.mp3"
        audio_path = f"static/{audio_filename}"
        
        # Make sure the static directory exists
        os.makedirs('static', exist_ok=True)
        
        # Generate the audio file
        speak_text(generated_response, filename=audio_path)

        return jsonify({
            'status': 'success', 
            'response': generated_response,
            'audio': url_for('static', filename=audio_filename)
        })

    except Exception as e:
        print(f"Error in send_message: {e}")  # Debug log
        return jsonify({'status': 'error', 'message': str(e)})
# @app.route('/voice_response', methods=['POST'])
# @login_required
# def voice_response():
#     import uuid  # Import uuid for generating unique filenames

#     data = request.json
#     user_message = data.get('message')

#     if user_message:
#         response_text = generate_response(user_message)
#         unique_id = uuid.uuid4().hex  # Generate a unique identifier
#         audio_filename = f"response_{session['user']['email']}_{unique_id}.mp3"
#         speak_text(response_text, filename=f"static/{audio_filename}")  # Generates the voice file
#         return jsonify({'status': 'success', 'response': response_text, 'audio': url_for('static', filename=audio_filename)})

#     return jsonify({'status': 'error', 'message': 'No message provided'})


@app.route('/voice_response', methods=['POST'])
@login_required
def voice_response():
    data = request.json
    user_message = data.get('message')

    if user_message:
        response_text = generate_response(user_message)
        audio_filename = f"response_{session['user']['email']}.mp3"
        speak_text(response_text, filename=f"static/{audio_filename}")  # Generates the voice file
        return jsonify({'status': 'success', 'response': response_text, 'audio': url_for('static', filename=audio_filename)})

    return jsonify({'status': 'error', 'message': 'No message provided'})

# @app.route('/voice_response', methods=['POST'])
# @login_required
# def voice_response():
#     data = request.json
#     user_message = data.get('message')

#     if user_message:
#         response_text = generate_response(user_message)
#         # Add timestamp to make filename unique
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
#         audio_filename = f"response_{session['user']['email']}_{timestamp}.mp3"
#         speak_text(response_text, filename=f"static/{audio_filename}")
#         return jsonify({
#             'status': 'success', 
#             'response': response_text, 
#             'audio': url_for('static', filename=audio_filename)
#         })

#     return jsonify({'status': 'error', 'message': 'No message provided'})
# @app.route('/send_message', methods=['POST'])
# @login_required
# def send_message():
#     data = request.json
#     user_message = data.get('message')
#     # prompt_template = data.get('promptTemplate', '')  # Get prompt template with empty default
#     # print(prompt_template)
#     prompt_template="""You are a witty and humorous assistant. Whenever I provide a word, your task is to create a clever, light-hearted, and original joke related to that word. Keep the humor fun and suitable for all audiences.

#             For example:

#             Word: Banana
#             Joke: Why did the banana go to the doctor? Because it wasn’t peeling well!"""

#     if not user_message:
#         return jsonify({'status': 'error', 'message': 'No message provided'})

#     try:
#         # Construct the full message with the prompt template
        
#         full_message = f"{prompt_template}\n\nUser Message: {user_message}"

#         llm = ChatGoogleGenerativeAI(
#             model="gemini-1.5-pro",
#             google_api_key=session['user']['api_key'],
#             temperature=0.5,
#             max_tokens=150,
#             timeout=10,
#             max_retries=1
#         )

#         response = llm.invoke(full_message)
#         generated_response = response.content

#         # Save chat history with the original user message
#         save_chat_history(session['user']['email'], user_message, generated_response)

#         # Generate audio response if needed
#         audio_filename = f"response_{session['user']['email']}.mp3"
#         speak_text(generated_response, filename=f"static/{audio_filename}")

#         return jsonify({
#             'status': 'success', 
#             'response': generated_response,
#             'audio': url_for('static', filename=audio_filename)
#         })

#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)



