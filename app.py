from flask import Flask, render_template
from flask_sock import Sock
import json

app = Flask(__name__)
sock = Sock(app)

sockets = {}

@app.route('/test')
def test():
    return render_template('index.html')

@sock.route('/')
def echo(sock):
    while True:
        data = sock.receive()

        obj = json.loads(data)
        print('messaging', obj['value'])

        if 'username' in obj and 'deviceId' in obj and obj['username'] and obj['deviceId']:
            username = obj['username']
            id = obj['deviceId']

            if username not in sockets:
                print('adding username ', username)
                sockets.update({username: []})

            if not is_added(sockets[username], id):
                sockets[username].append({"id": id, "sock": sock})
                print('added user with id', id)

            need_filter = False

            for item in sockets[username]:
                if not (item['id'] == id):
                    if item['sock'].connected:
                        item['sock'].send(data)
                    else:
                        need_filter = True

            if need_filter:
                sockets[username] = list(filter(has_connection, sockets[username]))
                print('remove disconnected users')

def has_connection(item):
    return item['sock'].connected

def is_added(items, id):
    for item in items:
        if item['id'] == id:
            return True
    return False
