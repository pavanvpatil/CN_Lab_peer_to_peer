# socket programming of manager

# author: 200030041 Pavan Kumar V Patil
# date: 1/4/2023
# course: Computer Networks CS348

import socket
from threading import Thread
import json
import time
import signal
import os

# create a socket object
Manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# server ip and port
server_ip = 'localhost'
server_port = 4000

# bind serversocket to the port
Manager_socket.bind((server_ip, server_port))

# list of active peers
active_peers = []


def check_peer_username(peer_username):
    """ This function is used to check if the username of the peer is already taken """

    for peer in active_peers:
        if peer[2] == peer_username:
            return True
    return False


def new_peer_joined(peer_socket, peer_address, peer_username):
    """ This function is used to add a new peer to the active peers list and update the active peers list of all the peers """

    global active_peers

    while (check_peer_username(peer_username)):
        peer_socket.send('Error in name'.encode())
        peer_username = peer_socket.recv(1024).decode()
        peer_username = peer_username.split(';')[1]

    time.sleep(0.1)
    peer_socket.send('Name accepted'.encode())
    print("Name accepted: ", peer_username)
    time.sleep(0.1)
    peer_address_temp = (peer_address[0], int(peer_socket.recv(1024).decode()))

    active_peers.append((peer_socket, peer_address_temp, peer_username))

    print("New peer joined the network: ", peer_address_temp, peer_username)
    updated_peer_list = json.dumps([(peer[1], peer[2]) for peer in active_peers])

    for peer in active_peers:
        try:
            peer[0].send('update_peer_list'.encode())
            time.sleep(0.1)
            peer[0].send(updated_peer_list.encode())
            print("sent updated list to peer: ", (peer[1], peer[2]))
        except (socket.error):
            print("Peer is no longer active: ", (peer[1], peer[2]))
            continue


def peer_leave(peer_socket):
    """ This function is used to remove a peer from the active peers list and update the active peers list of all the peers """

    global active_peers

    for peer in active_peers:
        if peer[0] == peer_socket:
            active_peers.remove(peer)
            print("Peer left the network: ", peer[2])
            updated_peer_list = json.dumps([(peer[1], peer[2]) for peer in active_peers])
            for peer in active_peers:
                try:
                    peer[0].send('update_peer_list'.encode())
                    time.sleep(0.1)
                    peer[0].send(updated_peer_list.encode())
                    print("sent updated list to peer: ", (peer[1], peer[2]))
                except (socket.error):
                    print("Peer is no longer active: ", (peer[1], peer[2]))
                    continue
            break

    peer_socket.close()


def start_peer_listen(peer_socket, peer_address):
    """ This function is used to listen to particluar peer. It listens for messages from the peer and takes appropriate action """

    while True:
        message = peer_socket.recv(1024).decode()
        print("message: ", message)

        if (message.split(';')[0] == 'Hello'):
            new_peer_joined(peer_socket, peer_address, message.split(';')[1])
            continue

        if (message == 'exit'):
            peer_socket.send('exit'.encode())
            time.sleep(0.1)
            peer_leave(peer_socket)
            break

        if message == "":
            peer_leave(peer_socket)
            break

def background_ping():
    """ This function is used to check for active peers, if a peer is not active, it is removed from the active peers list """

    global active_peers
    while True:
        print("checking for active peers...............")
        for peer in active_peers:
            try:
                socket_temp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_temp.settimeout(2)
                socket_temp.connect(peer[1])
                socket_temp.send('ping'.encode())
                time.sleep(0.1)
                socket_temp.recv(1024).decode()
                socket_temp.close()
            except (socket.error or socket.timeout):
                print("Peer is no longer active: ", (peer[1], peer[2]))
                peer_leave(peer[0])
                continue
        time.sleep(10)


def start_server():
    """ Starts the server and starts listening to peers, when new peer joins, it creates a new thread for that peer
     and it also starts a background thread to check for active peers """
    

    thread_background = Thread(target=background_ping)
    thread_background.daemon = True
    thread_background.start()


    # listen for incoming connections
    Manager_socket.listen(10)
    print('Manager is listening for incoming connections................\n')
    while True:
        (peer_socket, peer_address) = Manager_socket.accept()
        thread = Thread(target=start_peer_listen, args=(peer_socket, peer_address))
        thread.start()


def signal_handler(sig, frame):
    """ This function is used to handle the signal interrupt """

    print('You pressed Ctrl+C!')
    Manager_socket.close()
    os.kill(os.getpid(), signal.SIGKILL)

signal.signal(signal.SIGINT, signal_handler)

start_server()
