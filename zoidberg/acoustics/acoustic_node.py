import socket
import numpy as np
import threading
import queue

HOST = 'localhost'
PORT = 50007
all_data = queue.Queue()

def beagle_server(stop):
    """Open up a server than listend to the beagle whenever it has data"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        while not stop():
            conn, addr = s.accept()
            dout = []
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data: break
                    dout.append(data)
                # convert from bytes back to a numpy array
                p_atfc = np.frombuffer(b''.join(dout), dtype=np.complex64)
                p_atfc = p_atfc.reshape(-1, 3)
                all_data.put(p_atfc)


if __name__ == "__main__":
    t1 = threading.Thread(target=beagle_server, args=(lambda: stop_threads,))

    stop_threads = False
    current_pressure = None
    try:
        t1.start()
        while True:
            current_pressure = all_data.get()
            if current_pressure is not None:
                print(np.sum(current_pressure))
    except KeyboardInterrupt:
        stop_threads = True
