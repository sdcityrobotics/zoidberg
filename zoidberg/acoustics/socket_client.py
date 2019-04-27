import socket
import numpy as np
import pickle

HOST = 'localhost'
PORT = 50007

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    record = b''
    while True:
        data = s.recv(1024)
        if not data: break
        record += data
    reading = pickle.loads(record)

print(reading)
