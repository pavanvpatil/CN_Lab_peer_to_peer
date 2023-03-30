# socket programming for tcp server

import socket
from threading import Thread
import json
import time

# create a socket object
Manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# server ip and port
server_ip = 'localhost'
server_port = 8080

# bind serversocket to the port
Manager_socket.bind((server_ip, server_port))

# list of active peers
active_peers = []

# listen for incoming connections
Manager_socket.listen(1)
print('Manager is listening for incoming connections')


def new_peer_joined(peer_socket, peer_address):
    active_peers.append((peer_socket, peer_address))

    print("New peer joined the network: ", peer_address)
    updated_peer_list = json.dumps([peer[1] for peer in active_peers])

    for peer in active_peers:
        try:
            peer[0].send('update_peer_list'.encode())
            time.sleep(0.5)
            peer[0].send(updated_peer_list.encode())
            print("sent updated list to peer: ", peer[1])
        except (socket.error):
            print("Peer is no longer active: ", peer[1])
            continue


while True:
    (peer_socket, peer_address) = Manager_socket.accept()

    message = peer_socket.recv(1024).decode()

    print("message: ", message)

    if (message == 'Hello'):
        thread_A = Thread(target=new_peer_joined,
                          args=(peer_socket, peer_address))
        thread_A.start()
        thread_A.join()
