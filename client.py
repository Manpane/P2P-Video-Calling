import cv2
import socket
import threading
import requests
import numpy as np

BUFFER_SIZE = 65507

# signalling server
server_address = ('192.168.1.141', 2323)

signaling_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# UDP sockets for sending and receiving camera frames
socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

video_capture = cv2.VideoCapture(0)

connection_established = threading.Event()

def send_frames():
    while True:
        ret, frame = video_capture.read()

        frame = cv2.resize(frame,(360,240))

        _,encoded_frame = cv2.imencode('.jpg', frame)
        socket_send.sendto(encoded_frame, peer_address)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    socket_send.close()
    socket_receive.close()

def receive_frames():
    print("Started to receive the peer camera frames")
    while True:
        encoded_frame, _ = socket_receive.recvfrom(BUFFER_SIZE)

        frame = cv2.imdecode(np.frombuffer(encoded_frame, dtype=np.uint8), cv2.IMREAD_COLOR)
        try:
            cv2.imshow('Receiver', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except:
            print("Invalid Frame data received")

    socket_receive.close()

def establish_connection():
    signaling_socket.connect(server_address)

    my_ip = socket.gethostbyname(socket.gethostname())
    my_port = 5698

    device_info = f"{my_ip}:{my_port}"
    #sending my ip and port to segnalling server
    signaling_socket.send(device_info.encode())

    #receiving the peer's ip and port
    peer_info = signaling_socket.recv(1024).decode()
    print("Got peer info from signalling server: ",peer_info)
    peer_ip, peer_port = peer_info.split(':')

    #Closing the signalling socket connection now
    signaling_socket.close()

    global peer_address
    peer_address = (peer_ip, int(peer_port))

    #Now hole punching using UDP socket
    socket_send.sendto(b"Hello from peer", peer_address)
    #Ready to receive data
    socket_receive.bind(('0.0.0.0', my_port))

    connection_established.set()

def start_client():
    connection_established.wait()

    receive_thread = threading.Thread(target=receive_frames)
    receive_thread.start()

    send_frames()

    receive_thread.join()

    cv2.destroyAllWindows()

connection_thread = threading.Thread(target=establish_connection)
connection_thread.start()

start_client()

