import socket
import threading

#Every first message to the server is going to be a header of 64,
#which tells us the length of the next message
HEADER = 64
#Port
PORT = 5050
#get the IP address of the server by the server's name
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

#We created a socket of family INET with type SOCK_STREAM
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#we bind the socket to the address
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTIONG] {addr} connected.")

    connected = True
    while connected:
        #wait until something is received
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")

    conn.close()

def start():
    server.listen()
    print(f"[LISTENING] Server is listenning on {SERVER}")
    while True:
        #when a new connection occurs we store the addr
        conn, addr = server.accept()
        thread = threading.Thread(target = handle_client, args = (conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()