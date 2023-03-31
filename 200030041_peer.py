# socket programming in TCP for peer
import socket
import time
from threading import Thread
import json
import sys
import os
import shutil

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


def recieve_file_chunks(conn_peer_socket, offset, size_of_chunk):
    conn_peer_socket.send(
        ('file_required;'+str(size_of_chunk)+';'+str(offset)).encode())
    time.sleep(0.1)
    data = conn_peer_socket.recv(size_of_chunk)
    return data


def ask_and_recieve_file(file_name):
    global active_peer_list
    global name
    print("Asking for file............")
    peer_with_file = []
    size_of_file = 0
    for peer in active_peer_list:
        conn_peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_peer_socket.connect((peer[0][0], peer[0][1]))
        time.sleep(0.1)
        conn_peer_socket.send(('file_name;'+file_name).encode())
        time.sleep(0.1)
        message = conn_peer_socket.recv(1024).decode()
        if message == 'file_found':
            peer_with_file.append(conn_peer_socket)
            size_of_file = conn_peer_socket.recv(1024).decode()
            size_of_file = int(size_of_file)
            continue
        if message == 'file_not_found':
            conn_peer_socket.close()
            continue

    if len(peer_with_file) == 0:
        print("File not found")
        return
    else:
        print(len(peer_with_file))
        print("File found, downloading............")
        file = open("peername-"+name+"/"+file_name, 'wb')
        size_of_chunk = int(size_of_file/len(peer_with_file))
        offset = 0
        sum_of_chunks = 0
        for peer in range(len(peer_with_file)):
            if (peer == len(peer_with_file)-1):
                size_of_chunk = size_of_file - sum_of_chunks
            data = recieve_file_chunks(
                peer_with_file[peer], offset, size_of_chunk)
            file.write(data)
            offset = offset + size_of_chunk
            sum_of_chunks = sum_of_chunks + size_of_chunk
            peer_with_file[peer].close()
        file.close()


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
            ask_and_recieve_file(file_name)
            continue
        elif choice == '2':
            manager_peer_socket.send('exit'.encode())
            sys.exit(0)
        else:
            print("/---------Invalid choice---------/\n\n\n")
            continue


def peer_server_handler(conn_peer_socket):
    global name
    file_name = ''
    while True:
        message = conn_peer_socket.recv(1024).decode()
        if message.split(';')[0] == 'file_name':
            message = message.split(';')
            file_name = message[1]
            if os.path.isfile("./peername-"+name+"/"+file_name):
                print(file_name)
                conn_peer_socket.send('file_found'.encode())
                time.sleep(0.1)
                size_of_file = os.path.getsize("peername-"+name+"/"+file_name)
                conn_peer_socket.send(str(size_of_file).encode())
                continue
            else:
                conn_peer_socket.send('file_not_found'.encode())
                break

        if message == 'file_not_required':
            conn_peer_socket.close()
            break

        if message.split(';')[0] == 'file_required':
            message = message.split(';')
            no_of_bytes = int(message[1])
            offset = int(message[2])
            file = open("peername-"+name+"/"+file_name, 'rb')
            file.seek(offset)
            data = file.read(no_of_bytes)
            print(data)
            conn_peer_socket.send(data)
            file.close()
            continue


def peer_server(peer_socket):
    peer_socket.listen(20)
    while True:
        conn_peer_socket, conn_peer_address = peer_socket.accept()
        thread_D = Thread(target=peer_server_handler, args=(conn_peer_socket,))
        thread_D.start()


def main(manager_peer_socket, manager_address):
    global name
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
            shutil.rmtree("peername-"+name)
            os.kill(os.getpid(), 9)

        if message == '':
            print("Some thing gone wrong, Exiting............")
            shutil.rmtree("peername-"+name)
            os.kill(os.getpid(), 9)


main(manager_peer_socket, manager_address)
