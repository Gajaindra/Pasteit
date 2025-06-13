from flask import Flask, render_template, request, session, jsonify
from flask_socketio import SocketIO, emit
import uuid
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

notes = {}

def generate_token():
    return f"{random.randint(1000, 9999)}"

@app.route('/')
def index():
    note_id = session.get('note_id')
    content = session.get('content', '')
    token = notes.get(note_id, {}).get('token') if note_id else None
    return render_template('index.html', content=content, token=token)

@app.route('/save', methods=['POST'])
def save():
    content = request.form.get('content', '')
    session['content'] = content

    note_id = session.get('note_id')
    if not note_id:
        note_id = str(uuid.uuid4())[:8]
        session['note_id'] = note_id

    token = notes.get(note_id, {}).get('token', generate_token())
    notes[note_id] = {'content': content, 'token': token}

    # Emit content change to all connected clients
    socketio.emit('content_updated', {'content': content, 'token': token}, broadcast=True)

    return jsonify({'token': token})

@app.route('/get_content')
def get_content():
    note_id = session.get('note_id')
    content = ''
    token = None
    if note_id and note_id in notes:
        content = notes[note_id]['content']
        token = notes[note_id]['token']
        session['content'] = content
    return jsonify({'content': content, 'token': token})

@app.route('/refresh_token')
def refresh_token():
    note_id = session.get('note_id')
    if note_id in notes:
        token = generate_token()
        notes[note_id]['token'] = token
    return redirect(url_for('index'))

@app.route('/join', methods=['POST'])
def join():
    token = request.form['token']
    for note_id, note in notes.items():
        if note['token'] == token:
            session['note_id'] = note_id
            session['content'] = note['content']
            return redirect(url_for('index'))
    return redirect(url_for('index'))

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)
