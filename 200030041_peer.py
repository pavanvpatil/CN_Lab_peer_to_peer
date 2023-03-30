# socket programming in TCP for peer
import socket
import time
from threading import Thread
import json
import sys
from copy import deepcopy

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
accepted = False


def peer_features(peer_socket, manager_address):
    global name
    while True:
        print("Username: ", name)
        print("\nChoose an option: ")
        print("1. Ask for file")
        print("2. Exit")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            file_name = input("Enter file name: ")
            # peer_socket.send(('ask_file;' + file_name).encode())
            continue
        elif choice == 2:
            peer_socket.send('exit'.encode())
            sys.exit(0)
        else:
            print("/---------Invalid choice---------/\n\n\n")
            continue


def peer_client(peer_socket, manager_address):
    global name
    global accepted
    global active_peer_list
    peer_socket.connect(manager_address)

    peer_socket.send(('Hello;' + name).encode())

    while True:
        message = peer_socket.recv(1024).decode()

        # print("message: ", message)

        if message == 'update_peer_list':
            message = peer_socket.recv(1024).decode()
            temp_active_peer_list = json.loads(message)
            active_peer_list.clear()
            active_peer_list = temp_active_peer_list.copy()
            # print("updated_peer_list: ", active_peer_list)
            continue

        if message == 'Error in name':
            # print("User with same name already exists")
            name = input("Re-Enter your name: ")
            peer_socket.send(('Hello;' + name).encode())
            continue

        if message == 'Name accepted':
            accepted = True
            continue

        if message == 'exit':
            print("Exiting............")
            sys.exit(0)


def peer_server(peer_socket):
    peer_socket.listen(1)
    # print('Peer is listening for incoming connections................\n')
    while True:
        pass


# temp_peer_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
thread_A = Thread(target=peer_client, args=(peer_socket, manager_address))
thread_A.start()

# thread_B = Thread(target=peer_server, args=(peer_socket,))
# thread_B.start()

# temp_peer_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while not accepted:
    continue

thread_C = Thread(target=peer_features, args=(peer_socket, manager_address))
thread_C.start()

thread_A.join()
thread_C.join()
