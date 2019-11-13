import struct
import errno
from base64 import b64encode
from hashlib import sha1, md5
from socket import error as SocketError
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler

FIN    = 0x80
OPCODE = 0xf
MASKED = 0x80
PAYLOAD_LEN = 0x7f
PAYLOAD_LEN_EXT16 = 0x7e
PAYLOAD_LEN_EXT64 = 0x7f

OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE_CONN = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xA

class API():
    def run_forever(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            self.server_close()
        except Exception as e:
            exit(1)

    def new_client(self, client, server):
        pass

    def client_left(self, client, server):
        pass

    def message_received(self, client, server, message):
        pass

    def set_fn_new_client(self, fn):
        self.new_client = fn

    def set_fn_client_left(self, fn):
        self.client_left = fn

    def set_fn_message_received(self, fn):
        self.message_received = fn

    def send_message(self, client, msg, opcode=OPCODE_TEXT):
        self._unicast_(client, msg, opcode)

    def send_message_to_all(self, msg, opcode=OPCODE_TEXT):
        self._multicast_(msg, opcode)

class WebsocketServer(ThreadingMixIn, TCPServer, API):
    allow_reuse_address = True
    daemon_threads = True

    clients = []
    id_counter = 0

    def __init__(self, port, host='0.0.0.0',):
        TCPServer.__init__(self, (host, port), WebSocketHandler)
        self.port = self.socket.getsockname()[1]
        print('Listening at port', port)

    def _message_received_(self, handler, msg):
        resp_msg = ""
        # print("Client(%d) send raw: %s" % (self.handler_to_client(handler)['id'], msg))
        arr_msg = msg.split()
        if (arr_msg[0] == "!echo"):
            arr_msg.pop(0)
            resp_msg = " ".join(arr_msg)
            client = self.handler_to_client(handler)
            self.send_message(client, resp_msg)
            # print("Client(%d) was given back: %s" % (self.handler_to_client(handler)['id'], resp_msg))
        elif (arr_msg[0] == "!submission"):
            f = open('client.zip', 'rb')
            resp_msg = f.read()
            f.close()
            client = self.handler_to_client(handler)
            self.send_message(client, resp_msg, OPCODE_BINARY)
            # print("Client(%d) was given back: %s" % (self.handler_to_client(handler)['id'], resp_msg))
            resp_msg = 'submission'
        else:
            real = msg
            received = md5(real).hexdigest()
            current = md5(open('client.zip','rb').read()).hexdigest()
            if (received == current):
                resp_msg = '1'
            else:
                resp_msg = '0'
            client = self.handler_to_client(handler)
            self.send_message(client, resp_msg)
            # print("Client(%d) was given back: %s" % (self.handler_to_client(handler)['id'], resp_msg))
        self.message_received(self.handler_to_client(handler), self, resp_msg)

    def _ping_received_(self, handler, msg):
        handler.send_pong(msg)

    def _pong_received_(self, handler, msg):
        pass

    def _new_client_(self, handler):
        self.id_counter += 1
        client = {
            'id': self.id_counter,
            'handler': handler,
            'address': handler.client_address
        }
        self.clients.append(client)
        self.new_client(client, self)

    def _client_left_(self, handler):
        client = self.handler_to_client(handler)
        self.client_left(client, self)
        if client in self.clients:
            self.clients.remove(client)

    def _unicast_(self, to_client, msg, opcode):
        to_client['handler'].send_message(msg, opcode)

    def _multicast_(self, msg, opcode):
        for client in self.clients:
            self._unicast_(client, msg, opcode)

    def handler_to_client(self, handler):
        for client in self.clients:
            if client['handler'] == handler:
                return client

class WebSocketHandler(StreamRequestHandler):
    def __init__(self, socket, addr, server):
        self.server = server
        StreamRequestHandler.__init__(self, socket, addr, server)

    def setup(self):
        StreamRequestHandler.setup(self)
        self.keep_alive = True
        self.handshake_done = False
        self.valid_client = False

    def handle(self):
        while self.keep_alive:
            if not self.handshake_done:
                self.handshake()
            elif self.valid_client:
                self.read_next_message()

    def read_bytes(self, num):
        return self.rfile.read(num)

    def read_next_message(self):
        try:
            b1, b2 = self.read_bytes(2)
        except SocketError as e:
            if e.errno == errno.ECONNRESET:
                self.keep_alive = 0
                return
            b1, b2 = 0, 0
        except ValueError as e:
            b1, b2 = 0, 0

        fin    = b1 & FIN
        opcode = b1 & OPCODE
        masked = b2 & MASKED
        payload_length = b2 & PAYLOAD_LEN

        if opcode == OPCODE_CLOSE_CONN:
            self.keep_alive = 0
            return
        if not masked:
            self.keep_alive = 0
            return
        if opcode == OPCODE_CONTINUATION:
            return
        elif opcode == OPCODE_TEXT:
            opcode_handler = self.server._message_received_
        elif opcode == OPCODE_BINARY:
            opcode_handler = self.server._message_received_
        elif opcode == OPCODE_PING:
            opcode_handler = self.server._ping_received_
        elif opcode == OPCODE_PONG:
            opcode_handler = self.server._pong_received_
        else:
            self.keep_alive = 0
            return

        if payload_length == 126:
            payload_length = struct.unpack(">H", self.rfile.read(2))[0]
        elif payload_length == 127:
            payload_length = struct.unpack(">Q", self.rfile.read(8))[0]

        masks = self.read_bytes(4)
        message_bytes = bytearray()
        for message_byte in self.read_bytes(payload_length):
            message_byte ^= masks[len(message_bytes) % 4]
            message_bytes.append(message_byte)
        
        try:
            opcode_handler(self, message_bytes.decode('utf8'))
        except Exception as e:
            opcode_handler(self, message_bytes)

    def send_message(self, message, opcode=OPCODE_TEXT):
        self.send_text(message, opcode)

    def send_pong(self, message):
        self.send_text(message, OPCODE_PONG)

    def send_text(self, message, opcode=OPCODE_TEXT):
        header = bytearray()

        if (type(message) == str):
            payload = message.encode()
        else:
            payload = message
        payload_length = len(payload)

        if payload_length < 126: # Normal payload
            header.append(FIN | opcode)
            header.append(payload_length)
        elif payload_length < 65536: # Extended payload
            header.append(FIN | opcode)
            header.append(PAYLOAD_LEN_EXT16)
            header.extend(struct.pack(">H", payload_length))
        elif payload_length < 18446744073709551616: # More extended payload
            header.append(FIN | opcode)
            header.append(PAYLOAD_LEN_EXT64)
            header.extend(struct.pack(">Q", payload_length))
        else:
            raise Exception("Pesan terlalu besar.")
            return

        self.request.send(header + payload)

    def read_http_headers(self):
        headers = {}
        http_get = self.rfile.readline().decode().strip()
        assert http_get.upper().startswith('GET')

        while True:
            header = self.rfile.readline().decode().strip()
            if not header:
                break
            head, value = header.split(':', 1)
            headers[head.lower().strip()] = value.strip()
        return headers

    def handshake(self):
        headers = self.read_http_headers()

        try:
            assert headers['upgrade'].lower() == 'websocket'
        except AssertionError:
            self.keep_alive = False
            return

        try:
            key = headers['sec-websocket-key']
        except KeyError:
            self.keep_alive = False
            return

        response = self.make_handshake_response(key)
        self.handshake_done = self.request.send(response.encode())
        self.valid_client = True
        self.server._new_client_(self)

    @classmethod
    def make_handshake_response(cls, key):
        return \
          'HTTP/1.1 101 Switching Protocols\r\n'\
          'Upgrade: websocket\r\n'              \
          'Connection: Upgrade\r\n'             \
          'Sec-WebSocket-Accept: %s\r\n'        \
          '\r\n' % cls.calculate_response_key(key)

    @classmethod
    def calculate_response_key(cls, key):
        GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        hash = sha1(key.encode() + GUID.encode())
        response_key = b64encode(hash.digest()).strip()
        return response_key.decode('ASCII')

    def finish(self):
        self.server._client_left_(self)
