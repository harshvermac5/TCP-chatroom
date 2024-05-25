import socket
import threading

nickname = input('Choose a nickname: ')

# AF_INET stands for Address Family Internet.
# It specifies that the socket is intended to communicate over IPv4, the fourth version of the Internet Protocol
# SOCK_STREAM indicates that the socket type is stream-oriented.
# It implies that the socket will use the Transmission Control Protocol (TCP).
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

running = True  # A flag to indicate whether the client is running

def receive():
    # The global statement in Python is used to declare that a variable defined inside a function or block of code refers to a global variable, rather than a local one.
    global running
    while running:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except OSError:
            print('An error occurred!')
            running = False
            client.close()
            break

def write():
    global running
    while running:
        try:
            message = f'{nickname}: {input("")}'
            client.send(message.encode('ascii'))
        except OSError:
            print('Unable to send message!')
            running = False
            client.close()
            break

# The line receive_thread = threading.Thread(target=receive) is used to create a new thread in Python that will execute the receive function concurrently. This allows your program to perform multiple tasks simultaneously, such as listening for incoming messages while handling other operations.
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
