from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
import uuid
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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

    return jsonify({'token': token})

@app.route('/refresh_token')
def refresh_token():
    note_id = session.get('note_id')
    if note_id in notes:
        token = generate_token()
        notes[note_id]['token'] = token
        flash("Token refreshed successfully.")
    return redirect(url_for('index'))

@app.route('/join', methods=['POST'])
def join():
    token = request.form['token']
    for note_id, note in notes.items():
        if note['token'] == token:
            session['note_id'] = note_id
            session['content'] = note['content']
            flash("Note loaded successfully.")
            return redirect(url_for('index'))

    flash("Invalid token.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
