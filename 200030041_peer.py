# socket programming in TCP for peer
import socket
from threading import Thread
import json

peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

manager_ip = 'localhost'
manager_port = 8080

peer_socket.connect((manager_ip, manager_port))

active_peer_list = []
name = input("Enter your name: ")

def updated_peer_list():
    global active_peer_list

    message = peer_socket.recv(1024).decode()
    temp_active_peer_list = json.loads(message)

    active_peer_list.clear()
    active_peer_list = temp_active_peer_list.copy()


peer_socket.send(('Hello' + name).encode())
while True:
    message = peer_socket.recv(1024).decode()

    print("message: ", message)

    if message == 'update_peer_list':
        thread_A = Thread(target=updated_peer_list)
        thread_A.start()
        print("updated_peer_list: ", active_peer_list)
        thread_A.join()

    if message == 'Error in name':
        print("User with same name already exists")
        name = input("Enter your name: ")
        peer_socket.send(('Hello' + name).encode())
