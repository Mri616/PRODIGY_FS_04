from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secret'
socketio = SocketIO(app)

DB = "users.db"

# --- User DB setup
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# --- Routes
@app.route('/')
def home():
    if 'username' in session:
        return redirect('/chat')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (uname, pwd))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = uname
            return redirect('/chat')
        else:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = ''
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        try:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (uname, pwd))
            conn.commit()
            conn.close()
            return redirect('/login')
        except:
            error = 'Username already exists'
    return render_template('register.html', error=error)

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect('/login')
    return render_template('chat.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# --- Socket.IO Events
@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'{username} has joined the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    msg = data['msg']
    username = data['username']
    emit('message', {'msg': msg, 'username': username}, room=room)

@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'{username} has left the room.'}, room=room)

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True)
