import threading
import socket
import hashlib
import base64
import time
import signal
import sys
import json
from .namespace import Namespace

class EmoticSocketIO:
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_counter = 0
        self.namespaces = {'/': Namespace('/')}
        self.running = True

    def start(self, host='localhost', port=8888):
        if self.host is None: self.host = host
        if self.port is None: self.port = port
        self.server.bind((self.host or host, self.port or port))
        self.server.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        signal.signal(signal.SIGINT, self.shutdown)
        
        ping_thread = threading.Thread(target=self.ping_clients)
        ping_thread.start()

        while self.running:
            try:
                client_socket, _ = self.server.accept()
                self.handshake(client_socket)
                self.client_counter += 1
                client_id = self.client_counter
                print(f"Client connected: Connection ID {client_id}")
                
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_id))
                client_thread.start()
            except KeyboardInterrupt:
                self.shutdown()

    def shutdown(self, signum=None, frame=None):
        print("Shutting down the server...")
        self.running = False

        for namespace in self.namespaces.values():
            for client_socket in namespace.clients:
                try:
                    client_socket.close()
                except:
                    pass
        
        self.server.close()
        sys.exit(0)

    def handshake(self, client_socket):
        data = client_socket.recv(2048).decode('utf-8')
        headers = data.split('\r\n')
        key = None

        for header in headers:
            if "Sec-WebSocket-Key" in header:
                key = header.split(": ")[1]

        if key is None:
            return  # Invalid handshake, close the connection

        response_key = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode('utf-8')

        response = "HTTP/1.1 101 Switching Protocols\r\n" \
                "Upgrade: websocket\r\n" \
                "Connection: Upgrade\r\n" \
                "Server: Emonic 1.0.1/Python 3.9\r\n" \
                f"Sec-WebSocket-Accept: {response_key}\r\n\r\n"

        client_socket.send(response.encode('utf-8'))

    def handle_client(self, client_socket, client_id):
        while True:
            try:
                opcode, data = self.receive_data(client_socket)
                if opcode is None:
                    break
                if opcode == 8:  # Connection close
                    self.handle_close(client_socket)
                    break
                elif opcode == 9:  # Ping
                    self.handle_ping(client_socket)
                elif opcode == 10:  # Pong
                    self.handle_pong(client_socket)
                elif opcode == 1:  # Text message
                    self.handle_message(data, client_socket, client_id)
                elif opcode == 2:  # Binary message
                    self.handle_binary(data, client_socket, client_id)
            except:
                break
        
        client_socket.close()

    def receive_data(self, client_socket):
        data = client_socket.recv(2048)
        if not data:
            return None, None
        
        opcode = data[0] & 0x0F
        payload_length = data[1] & 0x7F
        
        if payload_length == 126:
            payload_length = int.from_bytes(data[2:4], byteorder="big")
            mask_index = 4
        elif payload_length == 127:
            payload_length = int.from_bytes(data[2:10], byteorder="big")
            mask_index = 10
        else:
            mask_index = 2
        
        masks = data[mask_index:mask_index+4]
        payload_data = data[mask_index+4:]
        
        decoded_data = bytearray()
        for i in range(len(payload_data)):
            decoded_data.append(payload_data[i] ^ masks[i % 4])
        
        return opcode, decoded_data

    def send_message(self, client_socket, message):
        encoded_message = self.encode_message(1, message)
        client_socket.send(encoded_message)

    def send_binary(self, client_socket, data):
        encoded_data = self.encode_message(2, data)
        client_socket.send(encoded_data)

    def send_ping(self, client_socket):
        ping_frame = bytearray([0x89, 0x00])
        client_socket.send(ping_frame)

    def send_pong(self, client_socket):
        pong_frame = bytearray([0x8A, 0x00])
        client_socket.send(pong_frame)

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

    def handle_message(self, message, client_socket, client_id):
        message_str = message.decode('utf-8')  # Decode the bytearray to a string
        print(f"Received text message from client {client_id}: {message_str}")

    def handle_binary(self, data, client_socket, client_id):
        print(f"Received binary data from client {client_id}: {data}")
        self.send_binary(client_socket, b"Server received your binary data")

    def handle_ping(self, client_socket):
        print("Received Ping from client")
        self.send_pong(client_socket)

    def handle_pong(self, client_socket):
        print("Received Pong from client")

    def handle_close(self, client_socket):
        print("Connection closed by client")

    def ping_clients(self):
        while True:
            time.sleep(30)
            for client_socket in self.namespaces['/'].clients:
                try:
                    self.send_ping(client_socket)
                except:
                    client_socket.close()

    def get_namespace(self, namespace_name):
        if namespace_name not in self.namespaces:
            self.namespaces[namespace_name] = Namespace(namespace_name)
        return self.namespaces[namespace_name]

    def on(self, event_name):
        def decorator(callback):
            default_namespace = self.get_namespace('/')
            default_namespace.register_event_handler(event_name, callback)
        return decorator

    def emit(self, event_name, data, client_socket=None):
        if client_socket:
            self.send_message(client_socket, json.dumps({'event': event_name, 'data': data}))
        else:
            default_namespace = self.get_namespace('/')
            default_namespace.emit_to_all(json.dumps({'event': event_name, 'data': data}))

    def broadcast(self, event_name, data, sender_socket=None):
        default_namespace = self.get_namespace('/')
        default_namespace.broadcast_to_others(json.dumps({'event': event_name, 'data': data}), sender_socket)

    def emit_to_namespace(self, namespace_name, event_name, data, client_socket=None):
        namespace = self.get_namespace(namespace_name)
        if client_socket:
            self.send_message(client_socket, json.dumps({'event': event_name, 'data': data}))
        else:
            namespace.emit_to_all(json.dumps({'event': event_name, 'data': data}))

    def broadcast_to_namespace(self, namespace_name, event_name, data, sender_socket=None):
        namespace = self.get_namespace(namespace_name)
        namespace.broadcast_to_others(json.dumps({'event': event_name, 'data': data}), sender_socket)

    def broadcast_except_sender(self, event_name, data, sender_socket):
        default_namespace = self.get_namespace('/')
        default_namespace.broadcast_to_others_except_sender(
            json.dumps({'event': event_name, 'data': data}), sender_socket
        )

    def emit_to_all_clients(self, event_name, data):
        default_namespace = self.get_namespace('/')
        default_namespace.emit_to_all_clients(json.dumps({'event': event_name, 'data': data}))

    def close_all_clients(self):
        default_namespace = self.get_namespace('/')
        default_namespace.close_all_clients()

    def close_client(self, client_socket):
        default_namespace = self.get_namespace('/')
        default_namespace.close_client(client_socket)

    def send_to_client(self, client_socket, event_name, data):
        default_namespace = self.get_namespace('/')
        default_namespace.send_to_client(client_socket, event_name, data)

    def join_room(self, client_socket, room_name):
        default_namespace = self.get_namespace('/')
        default_namespace.join_room(client_socket, room_name)

    def leave_room(self, client_socket, room_name):
        default_namespace = self.get_namespace('/')
        default_namespace.leave_room(client_socket, room_name)

    def broadcast_to_room(self, room_name, event_name, data, exclude_socket=None):
        default_namespace = self.get_namespace('/')
        default_namespace.broadcast_to_room(room_name, event_name, data, exclude_socket)

    def disconnect(self, client_socket):
        default_namespace = self.get_namespace('/')
        default_namespace.disconnect_client(client_socket)

    def send_to_all_clients(self, event_name, data):
        default_namespace = self.get_namespace('/')
        default_namespace.send_to_all_clients(event_name, data)

    def emit_with_ack(self, client_socket, event_name, data, ack_callback=None):
        default_namespace = self.get_namespace('/')
        default_namespace.emit_with_ack(client_socket, event_name, data, ack_callback)

    def use(self, middleware_function):
        default_namespace = self.get_namespace('/')
        default_namespace.use(middleware_function)