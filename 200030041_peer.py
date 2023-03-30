# socket programming in TCP for peer
import socket
import time
from threading import Thread
import json

peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

manager_address = ('localhost', 4000)

active_peer_list = []
port = int(input("Enter your port: "))

while True:
    try:
        peer_socket.bind(('localhost', port))
        break
    except:
        print("Port already in use")
        port = int(input("Re-Enter your port: "))
        continue

peer_address = ('localhost', port)


name = input("Enter your name: ")


def peer_client(peer_socket, manager_address):
    global name
    global active_peer_list
    peer_socket.connect(manager_address)
    peer_socket.send(('Hello;' + name).encode())

    while True:
        message = peer_socket.recv(1024).decode()

        print("message: ", message)

        if message == 'update_peer_list':
            message = peer_socket.recv(1024).decode()
            temp_active_peer_list = json.loads(message)
            active_peer_list.clear()
            active_peer_list = temp_active_peer_list.copy()
            print("updated_peer_list: ", active_peer_list)
            continue

        if message == 'Error in name':
            print("User with same name already exists")
            name = input("Re-Enter your name: ")
            peer_socket.send(('Hello;' + name).encode())
            time.sleep(0.1)
            continue

def peer_server(peer_socket):
    peer_socket.listen(1)
    print('Peer is listening for incoming connections................\n')
    while True:
        pass


thread_A = Thread(target=peer_client, args=(peer_socket, manager_address))
thread_A.start()
thread_A.join()
