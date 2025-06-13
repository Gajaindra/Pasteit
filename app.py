from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import uuid
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

notes = {}

def generate_token():
    return str(random.randint(1000, 9999))

@app.route('/')
def index():
    note_id = session.get('note_id')
    content = ''
    token = None
    if note_id and note_id in notes:
        content = notes[note_id]['content']
        token = notes[note_id]['token']
    return render_template('index.html', content=content, token=token)

@app.route('/join', methods=['POST'])
def join():
    token = request.form['token']
    for note_id, note in notes.items():
        if note['token'] == token:
            session['note_id'] = note_id
            return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/refresh_token')
def refresh_token():
    note_id = session.get('note_id')
    if note_id in notes:
        new_token = generate_token()
        notes[note_id]['token'] = new_token
        socketio.emit('token_updated', {'token': new_token}, room=note_id)
    return redirect(url_for('index'))

@socketio.on('connect')
def on_connect():
    print("Client connected")

@socketio.on('join_room')
def on_join(data=None):
    note_id = session.get('note_id')
    if note_id:
        join_room(note_id)
        if note_id in notes:
            emit('content_update', {
                'content': notes[note_id]['content'],
                'token': notes[note_id]['token']
            }, room=request.sid)

@socketio.on('update_content')
def on_update(data):
    content = data.get('content', '')
    note_id = session.get('note_id')
    if note_id:
        if note_id not in notes:
            notes[note_id] = {'content': content, 'token': generate_token()}
        else:
            notes[note_id]['content'] = content
        emit('content_update', {
            'content': content,
            'token': notes[note_id]['token']
        }, room=note_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)
