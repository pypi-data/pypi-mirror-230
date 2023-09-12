import json

class Namespace:
    def __init__(self, name):
        self.name = name
        self.clients = []
        self.event_handlers = {}
        self.rooms = {}
        self.middlewares = []

    def use(self, middleware_function):
        self.middlewares.append(middleware_function)

    def register_event_handler(self, event_name, callback):
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(callback)

    def unregister_event_handler(self, event_name, callback):
        if event_name in self.event_handlers:
            self.event_handlers[event_name].remove(callback)

    def emit_to_all(self, message, sender_socket=None):
        encoded_message = self.encode_message(1, message)
        
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send(encoded_message)
                except:
                    client_socket.close()
                    self.unregister_client(client_socket)

    def broadcast_to_others(self, message, sender_socket=None):
        encoded_message = self.encode_message(1, message)
        
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send(encoded_message)
                except:
                    client_socket.close()
                    self.unregister_client(client_socket)

    def register_client(self, client_socket):
        self.clients.add(client_socket)

    def unregister_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)

    def encode_message(self, opcode, message):
        message = message.encode('utf-8')
        message_length = len(message)
        if message_length <= 125:
            header = bytearray([0x80 | opcode, message_length])
        elif message_length <= 65535:
            header = bytearray([0x80 | opcode, 126]) + message_length.to_bytes(2, byteorder="big")
        else:
            header = bytearray([0x80 | opcode, 127]) + message_length.to_bytes(8, byteorder="big")
        return header + message
    
    def broadcast_to_others_except_sender(self, message, sender_socket):
        encoded_message = self.encode_message(1, message)
        
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send(encoded_message)
                except:
                    client_socket.close()
                    self.unregister_client(client_socket)

    def emit_to_all_clients(self, message):
        encoded_message = self.encode_message(1, message)
        
        for client_socket in self.clients:
            try:
                client_socket.send(encoded_message)
            except:
                client_socket.close()
                self.unregister_client(client_socket)

    def close_all_clients(self):
        for client_socket in self.clients:
            try:
                client_socket.close()
            except:
                pass
        self.clients.clear()

    def close_client(self, client_socket):
        if client_socket in self.clients:
            try:
                client_socket.close()
            except:
                pass
            self.clients.remove(client_socket)

    def send_to_client(self, client_socket, event_name, data):
        encoded_message = self.encode_message(1, json.dumps({'event': event_name, 'data': data}))
        try:
            client_socket.send(encoded_message)
        except:
            self.close_client(client_socket)

    def join_room(self, client_socket, room_name):
        self.rooms[room_name].add(client_socket)

    def leave_room(self, client_socket, room_name):
        if room_name in self.rooms and client_socket in self.rooms[room_name]:
            self.rooms[room_name].remove(client_socket)

    def broadcast_to_room(self, room_name, event_name, data, exclude_socket=None):
        if room_name in self.rooms:
            encoded_message = self.encode_message(1, json.dumps({'event': event_name, 'data': data}))
            for client_socket in self.rooms[room_name]:
                if client_socket != exclude_socket:
                    try:
                        client_socket.send(encoded_message)
                    except:
                        self.close_client(client_socket)

    def disconnect_client(self, client_socket):
        self.close_client(client_socket)

    def send_to_all_clients(self, event_name, data):
        encoded_message = self.encode_message(1, json.dumps({'event': event_name, 'data': data}))
        for client_socket in self.clients:
            try:
                client_socket.send(encoded_message)
            except:
                self.close_client(client_socket)

    def emit_with_ack(self, client_socket, event_name, data, ack_callback=None):
        encoded_message = self.encode_message(1, json.dumps({'event': event_name, 'data': data}))
        try:
            client_socket.send(encoded_message)
        except:
            self.close_client(client_socket)
            return

        if ack_callback:
            response_opcode, response_data = self.receive_data(client_socket)
            if response_opcode == 1:
                response_data = json.loads(response_data.decode('utf-8'))
                ack_callback(response_data)

    def handle_event(self, event_name, data, client_socket):
        for middleware in self.middlewares:
            data = middleware(event_name, data, client_socket)

        if event_name in self.event_handlers:
            for callback in self.event_handlers[event_name]:
                callback(data, client_socket)

    def send_error(self, client_socket, error_message):
        error_data = {"error": error_message}
        self.send_to_client(client_socket, "error", error_data)