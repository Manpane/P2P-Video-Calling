import socket

# Create a TCP socket for signaling
signaling_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server address
server_address = ('', 2323)
signaling_socket.bind(server_address)
signaling_socket.listen(1)

# Dictionary to store client information
clients = {}
connections = []
print("Server is listening at port 2323")
try:
    while True:
        # Accept client connection
        client_socket, address = signaling_socket.accept()
        print(f"Client connected {address}")

        # Receive client information
        client_info = client_socket.recv(1024)
        print(f"Received client info {client_info}")

        connections.append(client_socket)
        clients[client_socket] = client_info

        if len(connections)==2:
            for conn in connections:
                peer_info = clients[ [c for c in clients.keys() if c!=conn][0] ]
                conn.send(peer_info)
                conn.close()
            connections = []
            clients = {}
        

except KeyboardInterrupt:
    # Close the signaling socket
    signaling_socket.close()
