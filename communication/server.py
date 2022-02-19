import socket
import threading
import paho.mqtt.client as mqtt
import json
import eventlet
import socketio


messageQueue = []

sio = socketio.Server(cors_allowed_origins='*')

app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)

@sio.on('msg')
def message(sid, data):
    print('message ', data)

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

@sio.on('getData')
def getData(sid, data):
    print('message ', messageQueue)
    while len(messageQueue) > 0:
        sio.emit('setData', messageQueue.pop(0))

# #Every first message to the server is going to be a header of 64,
# #which tells us the length of the next message
# HEADER = 64
# #Port
# PORT = 5050
# #get the IP address of the server by the server's name
# SERVER = socket.gethostbyname(socket.gethostname())
# ADDR = (SERVER, PORT)
# FORMAT = 'utf-8'
# DISCONNECT_MESSAGE = "!DISCONNECT"
# ACK_TEXT = 'text_received'

# #We created a socket of family INET with type SOCK_STREAM
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# #we bind the socket to the address
# server.bind(ADDR)

# def handle_client(conn, addr):
#     print(f"[NEW CONNECTIONG] {addr} connected.")

#     connected = True
#     while connected:
#         #wait until something is received
#         # print("Gonna send?", len(messageQueue))
#         # msg_length = conn.recv(HEADER).decode(FORMAT)
#         # if msg_length:
#         #     msg_length = int(msg_length)
#         #     msg = conn.recv(msg_length).decode(FORMAT)
#         #     if msg == DISCONNECT_MESSAGE:
#         #         connected = False

#         #     print(f"[{addr}] {msg}")
        
#         print("Gonna send?", len(messageQueue))
#         if len(messageQueue):
#             conn.sendall(messageQueue.pop(0))
#             # receive acknowledgment from the server
#             # encodedAckText = conn.recv(1024)
#             # ackText = encodedAckText.decode('utf-8')

#             # # log if acknowledgment was successful
#             # if ackText == ACK_TEXT:
#             #     print('server acknowledged reception of text')
#             # else:
#             #     print('error: server has sent back ' + ackText)

#     conn.close()

# def start():
#     server.listen()
#     print(f"[LISTENING] Server is listenning on {SERVER}")
#     while True:
#         #when a new connection occurs we store the addr
#         conn, addr = server.accept()
#         # handle_client(conn, addr)
#         # print("Active connection - 1")
#         thread = threading.Thread(target = handle_client, args = (conn, addr))
#         thread.start()
#         print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

######################################################
#               START OF MQTT SET UP                 #
######################################################
def on_message(client, userdata, message) :
    msg_decoced = str(message.payload.decode("utf-8", "ignore"))
    # m_in=json.loads(msg_decoced)
    # print(m_in)
    #print("Received message:{} on topic{}".format(message.payload, message.topic))
    messageQueue.append(msg_decoced)
    print(len(messageQueue))

def on_disconnect(client, userdata,rc=0):
    client.loop_stop()

def on_publish(client, userdata, result):
    #print("published data is: ")
    pass

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Connection failed")
 
Connected = False   #global variable for the state of the connection

# Creating the mqtt client
client = mqtt.Client()

# Callback functions
client.on_message = on_message
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_connect= on_connect

# Provides the private key/certificats needed to make a secure connection
#client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt", keyfile="client.key")

# Connect to port 8884 in order to make a secure connection 8884
client.connect("146.169.163.5",port=1883)

#subscribe to that topic
client.subscribe("IC.embedded/GROUP_NAME/#")

# Starts a new thread, that calls the loop method at regular intervals for you.
# It also handles re-connects automatically.
client.loop_start()

######################################################
#                 END OF MQTT SET UP                 #
######################################################

print("[STARTING] server is starting...")
# start()
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)