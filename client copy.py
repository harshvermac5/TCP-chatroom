import socket
import threading

nickname = input('Choose a nickname: ')
if nickname == 'admin':
    password = input('Enter password for admin: ')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

running = True  # A flag to indicate whether the client is running

def receive():
    global running
    while running:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                if next_message == 'PASSWD':
                    client.send(password.encode('ascii'))
                    response = client.recv(1024).decode('ascii')
                    if response == 'REFUSE':
                        print('Connection refused: wrong password!')
                        running = False
                elif next_message == 'BAN':
                    print('Connection refused: you are banned!')
                    running = False
            else:
                print(message)
        except OSError as e:
            print(f'An error occurred: {e}')
            running = False
            client.close()
            break

def write():
    global running
    while running:
        try:
            message = input()
            if message.startswith('/'):
                if nickname == 'admin':
                    if message.startswith('/kick'):
                        client.send(f'KICK {message[6:]}'.encode('ascii'))
                    elif message.startswith('/ban'):
                        client.send(f'BAN {message[5:]}'.encode('ascii'))
                else:
                    print('Commands can only be executed by admin!')
            else:
                client.send(f'{nickname}: {message}'.encode('ascii'))
        except OSError as e:
            print(f'Unable to send message: {e}')
            running = False
            client.close()
            break

# Create and start the threads for receiving and writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
