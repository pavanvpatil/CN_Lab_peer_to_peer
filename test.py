import os

file_name = input("Enter file name: ")
name = input("Enter name: ")
print(os.path.isfile("./peername-"+name+"/"+file_name))

print(os.path.exists("./peername-"+name+"/"+file_name))