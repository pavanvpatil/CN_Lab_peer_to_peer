# socket programming in TCP for peer

# author: 200030041 Pavan Kumar V Patil
# date: 1/4/2023
# course: Computer Networks CS348


import socket
import time
from threading import Thread
import json
import sys
import os
import shutil
import random

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


def recieve_file_chunks(conn_peer_socket, offset, number_of_chunks, size_of_chunk, file_data, index,error_index):
    for i in range(number_of_chunks):
        try:
            conn_peer_socket.send(('file_required;'+str(size_of_chunk)+';'+str(offset)).encode())
            conn_peer_socket.settimeout(5)
            data = conn_peer_socket.recv(size_of_chunk)
            file_data[index] = data
            offset = offset + size_of_chunk
            index = index + 1
        except(socket.timeout or socket.error):
            error_index.append((conn_peer_socket, index, offset, size_of_chunk))
            return

def check_and_correct_file_data(file_data, error_index,peer_with_file):
    while len(error_index) != 0:
        for error in error_index:
            peer_with_file.remove(error[0])

        if(len(peer_with_file) == 0):
            print("File downloading failed")
            return
        

        temp_error_index = []
        for error in error_index:
            conn_peer_socket = random.choice(peer_with_file)
            index = error[1]
            offset = error[2]
            size_of_chunk = error[3]
            try:
                conn_peer_socket.send(('file_required;'+str(size_of_chunk)+';'+str(offset)).encode())
                conn_peer_socket.settimeout(5)
                data = conn_peer_socket.recv(size_of_chunk)
                file_data[index] = data
                error_index.remove(error)
            except(socket.timeout or socket.error):
                temp_error_index.append((conn_peer_socket, index, offset, size_of_chunk))
                continue

        error_index = temp_error_index

    


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
        number_of_chunks = 100
        size_of_chunk = int(size_of_file/number_of_chunks)
        if (size_of_file % number_of_chunks != 0):
            number_of_chunks = number_of_chunks + 1
        if (size_of_file < 100):
            size_of_chunk = size_of_file
        offset = 0
        sum_of_chunks = 0
        threads = []
        file_data = [b'' for i in range(number_of_chunks)]
        peer_number_of_chunks = [0 for i in range(len(peer_with_file))]
        index = 0

        for peer in range(len(peer_with_file)):
            peer_number_of_chunks[peer] = int(
                number_of_chunks/len(peer_with_file))
            sum_of_chunks = sum_of_chunks + peer_number_of_chunks[peer]

        if (sum_of_chunks < number_of_chunks):
            peer_number_of_chunks[0] = peer_number_of_chunks[0] + \
                (number_of_chunks - sum_of_chunks)

        error_index = []

        for peer in range(len(peer_with_file)):
            t = Thread(target=recieve_file_chunks, args=(peer_with_file[peer], offset, peer_number_of_chunks[peer], size_of_chunk, file_data, index, error_index))
            t.start()
            threads.append(t)
            offset = offset + peer_number_of_chunks[peer]*size_of_chunk
            index = index + peer_number_of_chunks[peer]

        for i in range(len(threads)):
            threads[i].join()

        if(len(error_index) != 0):
            check_and_correct_file_data(file_data, error_index,peer_with_file)

        if(len(peer_with_file) == 0):
            return
        
        file = open("peername-"+name+"/"+file_name, 'wb')
        for i in range(number_of_chunks):
            file.write(file_data[i])
        file.close()
        print("File downloaded successfully")
        return


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
            if(os.path.isfile("./peername-"+name+"/"+file_name)):
                print("File already exists")
                continue
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
            conn_peer_socket.send(data)
            file.close()
            continue

        if message == 'ping':
            conn_peer_socket.send('pong'.encode())
            conn_peer_socket.close()
            break


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
