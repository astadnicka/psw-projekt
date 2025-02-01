from flask import Blueprint, jsonify, request
from flask_socketio import join_room, leave_room, emit

chat_bp = Blueprint("chat", __name__)

users = {}

def init_socketio(socketio):
    @socketio.on('join')
    def handle_join(data):
        username = data['username']
        room = data['room']
        join_room(room)  
        users[request.sid] = {'username': username, 'room': room}
        

    @socketio.on('send_message')
    def handle_send_message(data):
        room = users[request.sid]['room']
        username = users[request.sid]['username']
        emit('message', {
            'username': username,
            'message': data['message']
        }, room=room)  

    # @socketio.on('disconnect')
    # def handle_disconnect():
    #     user = users.pop(request.sid, None)
    #     if user:
    #         room = user['room']
    #         username = user['username']
    #         emit('message', {
    #             'username': 'System',
    #             'message': f'{username} has left the room.'  # Wiadomość o wyjściu użytkownika
    #         }, room=room)

def register_chat_blueprint(app, socketio):
    app.register_blueprint(chat_bp)
    init_socketio(socketio)
