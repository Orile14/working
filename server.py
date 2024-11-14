import socket
import sys

def lookup_in_zone_file(domain, zone_file):
    print(f"Looking up domain '{domain}' in zone file '{zone_file}'...")
    with open(zone_file, 'r') as file:
            for line in file:
                # Split each line into domain, IP, and classification
                parts = line.strip().split(',')
                print(f"Processing line: {line.strip()}")
                if len(parts) == 3:
                    file_domain, ip_address, classification = parts
                    if file_domain == domain:
                        print(f"Found domain {domain} with IP address {ip_address}")
                        return ip_address  # Return the IP address if found
    with open(zone_file, 'r') as file:
            for line in file:
                # Split each line into domain, IP, and classification
                parts = line.strip().split(',')
                print(f"Processing line: {line.strip()}")
                if len(parts) == 3:
                    file_domain, ip_address, classification = parts
                    if domain.endswith(file_domain):
                        print(f"Found NS domain {domain} with IP address {ip_address}")
                        return ip_address  # Return the IP address if found
    print(f"Domain {domain} not found in zone file.")

def main(myPort, zoneFileName):
    print(f"Starting server on port {myPort} with zone file '{zoneFileName}'...")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', myPort))
    print(f"Server listening on port {myPort}...")

    while True:
        data, addr = s.recvfrom(1024)
        domain = data.decode().strip()  # Decode the received data to get the domain
        print(f"Received query for domain: {domain} from {addr}")

        # Look up the domain in the zone file
        ip_address = lookup_in_zone_file(domain, zoneFileName)
        
        if ip_address:
            response = ip_address
            print(f"Responding with IP address: {response}")
        else:
            response = "non-existent domain"
            print(f"Responding with error: {response}")
        
        s.sendto(response.encode(), addr)  # Send back the response

if _name_ == "_main_":
    # Check if the correct number of arguments is passed
    if len(sys.argv) != 3:
        print("Usage: python server.py [myPort] [zoneFileName]")
        sys.exit(1)

    # Parse command-line arguments
    myPort = int(sys.argv[1])
    zoneFileName = sys.argv[2]

    main(myPort, zoneFileName)
