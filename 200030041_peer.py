# socket programming in TCP for peer
import socket
import time
from threading import Thread
import json
import sys
import os

manager_peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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


def peer_features(manager_peer_socket):
    global name
    while True:
        print("Username: ", name)
        print("\nChoose an option: ")
        print("1. Ask for file")
        print("2. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            file_name = input("Enter file name: ")
            # manager_peer_socket.send(('ask_file;' + file_name).encode())
            continue
        elif choice == '2':
            manager_peer_socket.send('exit'.encode())
            sys.exit(0)
        else:
            print("/---------Invalid choice---------/\n\n\n")
            continue


def peer_server(peer_socket):
    peer_socket.listen(1)
    while True:
        continue


def main(manager_peer_socket, manager_address):
    global name
    global accepted
    global active_peer_list
    global peer_address
    global peer_socket
    manager_peer_socket.connect(manager_address)

    manager_peer_socket.send(('Hello;' + name).encode())

    thread_C = Thread(target=peer_features, args=(manager_peer_socket,))
    thread_B = Thread(target=peer_server, args=(peer_socket,))

    while True:
        message = manager_peer_socket.recv(1024).decode()

        if message == 'update_peer_list':
            message = manager_peer_socket.recv(1024).decode()
            temp_active_peer_list = json.loads(message)
            active_peer_list.clear()
            active_peer_list = temp_active_peer_list.copy()
            continue

        if message == 'Error in name':
            name = input("Re-Enter your name: ")
            manager_peer_socket.send(('Hello;' + name).encode())
            continue

        if message == 'Name accepted':
            os.mkdir("peername-"+name)
            manager_peer_socket.send(str(peer_address[1]).encode())
            time.sleep(0.1)
            thread_C.start()
            thread_B.start()
            continue

        if message == 'exit':
            print("Exiting............")
            os.rmdir("peername-"+name)
            os.kill(os.getpid(), 9)

        if message == '':
            print("Some thing gone wrong, Exiting............")
            os.rmdir("peername-"+name)
            os.kill(os.getpid(), 9)


main(manager_peer_socket, manager_address)
