import socket
import sys

def lookup_in_zone_file(domain, zone_file):
    print(f"Looking up domain '{domain}' in zone file '{zone_file}'...")
    with open(zone_file, 'r') as file:
            for line in file:
                print(f"Processing line: {line.strip()}")

                # Split each line into domain, IP, and classification
                parts = line.strip().split(',')
                
                file_domain, ip_address, classification = parts
                if file_domain == domain:
                    print(f"Found domain {domain} with IP address {ip_address}")
                    return ip_address  
                    
    print(f"Domain {domain} not found in zone file.")
    with open(zone_file, 'r') as file:
            for line in file:
                print(f"Processing line: {line.strip()}")

                # Split each line into domain, IP, and classification
                parts = line.strip().split(',')
                
                file_domain, ip_address, classification = parts
                if domain.endswith(file_domain):
                    print(f"Found NS domain {domain} with IP address {ip_address}")
                    return line  
                    
    print(f"Domain {domain} not found in zone file.")
    return None

def main():
    myPort = int(sys.argv[1])
    zoneFileName = sys.argv[2]

    print(f"Starting server on port {myPort} with zone file '{zoneFileName}'...")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', myPort))

    print(f"Server listening on port {myPort}...")

    while True:
        data, addr = s.recvfrom(1024)
        domain = data.decode().strip()  

        print(f"Received query for domain: {domain} from {addr}")

        ip_address = lookup_in_zone_file(domain, zoneFileName)
        
        if ip_address:
            response = ip_address
            print(f"Responding with IP address: {response}")
        else:
            response = "non-existent domain"
            print(f"Responding with error: {response}")
        
        s.sendto(response.encode(), addr)  # Send back the response

if __name__ == "__main__":
    main()
