from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def chat():
    return render_template('chat.html')

@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)

@socketio.on('join')
def handleJoin(username):
    print(f'{username} has joined the chat.')
    send(f'{username} has joined the chat.', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)