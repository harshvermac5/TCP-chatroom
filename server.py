import threading
import socket

host = '127.0.0.1'
port = 55555

# AF_INET stands for Address Family Internet.
# It specifies that the socket is intended to communicate over IPv4, the fourth version of the Internet Protocol
# SOCK_STREAM indicates that the socket type is stream-oriented.
# It implies that the socket will use the Transmission Control Protocol (TCP).
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#  The bind() method associates the socket with a specific network address and port, setting up the local endpoint where the server will accept connections
server.bind((host, port))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024) # data = socket.recv(bufsize)
            if not message:
                raise Exception("Client disconnected")
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('ascii'))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname of the client is {nickname}')
        broadcast(f'{nickname} joined the chat'.encode('ascii'))
        client.send('Connected to the server!'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print('Server is listening...')
receive()
