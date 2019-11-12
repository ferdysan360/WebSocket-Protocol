from websocket_server import WebsocketServer

# Called for every client connecting (after handshake)
def new_client(client, server):
	print("Client(%d) connected" % client['id'])

# Called for every client disconnecting
def client_left(client, server):
	print("Client(%d) disconnected" % client['id'])

# Called when a client sends a message
def message_received(client, server, message):
	if len(message) > 150:
		message = message[:150]
	print("Client(%d) said: %s" % (client['id'], message))

PORT=5000
server = WebsocketServer(PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
