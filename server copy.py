import threading
import socket

host = '127.0.0.1'
port = 55555

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

# Lock for synchronizing access to shared resources
lock = threading.Lock()

def broadcast(message):
    with lock:
        for client in clients:
            try:
                client.send(message)
            except:
                pass  # Handle failed send here, e.g., remove client

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                raise ConnectionError("Client disconnected")
            
            decoded_message = message.decode('ascii')
            if decoded_message.startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = decoded_message[5:].strip()
                    kick_user(name_to_kick)
                else:
                    client.send('Command was refused!'.encode('ascii'))
            elif decoded_message.startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = decoded_message[4:].strip()
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned!')
                else:
                    client.send('Command was refused!'.encode('ascii'))
            else:
                broadcast(message)
        except Exception as e:
            print(f'Error: {e}')
            with lock:
                if client in clients:
                    index = clients.index(client)
                    clients.remove(client)
                    nickname = nicknames.pop(index)
                    client.close()
                    broadcast(f'{nickname} left the chat!'.encode('ascii'))
            break

def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        with open('bans.txt', 'r') as f:
            bans = f.read().splitlines()

        if nickname in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        if nickname == 'admin':
            client.send('PASSWD'.encode('ascii'))
            password = client.recv(1024).decode('ascii')

            with open('password.txt', 'r') as f:
                passwd = f.read().strip()

            if password != passwd:
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        with lock:
            nicknames.append(nickname)
            clients.append(client)

        print(f'Nickname of the client is {nickname}')
        broadcast(f'{nickname} joined the chat'.encode('ascii'))
        client.send('Connected to the server!'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    with lock:
        if name in nicknames:
            name_index = nicknames.index(name)
            client_to_kick = clients[name_index]
            clients.remove(client_to_kick)
            client_to_kick.send('You were kicked by admin!'.encode('ascii'))
            client_to_kick.close()
            nicknames.remove(name)
            broadcast(f'{name} was kicked by admin!'.encode('ascii'))

print('Server is listening...')
receive()
