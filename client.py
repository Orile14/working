import socket
import sys

# Read server IP and port from command-line arguments
server_ip = sys.argv[1]
server_port = int(sys.argv[2])

while True:
    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Take user input
    data = input("Enter message to send: ")
    
    # Send data to the server
    s.sendto(data.encode(), (server_ip, server_port))
    
    # Receive and print response from the server
    ans, addr = s.recvfrom(1024)
    print(f"Server response: {ans.decode()} from {addr}")
    
    # Close the socket
    s.close()