import socket
import sys
import time

# Cache to store domain-IP mappings
cache = {}
cache_time = {}

def resolve(domain, parent_ip, parent_port, cache_timeout, client_addr):
    print(f"Attempting to resolve domain: {domain}")
    
    # If the domain is in the cache and the cache is still valid, return the cached result
    if domain in cache:
        current_time = time.time()
        print(f"Domain {domain} found in cache. Checking cache validity...")
        
        if current_time - cache_time[domain] < cache_timeout:
            response = cache[domain]
            print(f"Cache is valid. Returning cached response: {response}")
            
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(response.encode(), client_addr)  # Send the cached response to the client
            return
        else:
            print(f"Cache expired for domain {domain}. Querying parent server.")

    print(f"Domain {domain} not in cache or cache expired. Querying parent server...")
    # Send the query to the parent server
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(domain.encode(), (parent_ip, parent_port))
        sock.settimeout(2)  # Timeout for waiting for the answer

        try:
            print(f"Sent query to {parent_ip}:{parent_port}")
            data, _ = sock.recvfrom(1024)
            response = data.decode()
            print(f"Received response from parent server: {response}")

            # Cache the response
            cache[domain] = response
            cache_time[domain] = time.time()

            print(f"Cached response for {domain}: {response}")

           
            sock.sendto(response.encode(), client_addr)  # Send the response to the client

            # If the response is an NS record, query the next server
            if response.endswith('NS'):
                ns_info = response.split(",")
                ns_ip, ns_port = ns_info[1].split(":")
                print(f"NS record found, querying next server: {ns_ip}:{ns_port}")
                resolve_from_ns(domain, ns_ip, int(ns_port), cache_timeout, client_addr)
        except socket.timeout:
            error_message = "non-existent domain"
            print(f"Error: {error_message} (timeout)")
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(error_message.encode(), client_addr)  # Send error message to the client

def resolve_from_ns(domain, ns_ip, ns_port, cache_timeout, client_addr):
    print(f"Resolving domain {domain} via NS server: {ns_ip}:{ns_port}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(domain.encode(), (ns_ip, ns_port))
        sock.settimeout(2)

        try:
            print(f"Sent query to {ns_ip}:{ns_port}")
            data, _ = sock.recvfrom(1024)
            response = data.decode()
            print(f"Received response from NS server: {response}")

            # Cache the response from NS
            cache[domain] = response
            cache_time[domain] = time.time()

            print(f"Cached NS response for {domain}: {response}")

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(response.encode(), client_addr)  # Send the response to the client
        except socket.timeout:
            error_message = "non-existent domain"
            print(f"Error: {error_message} (timeout)")
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(error_message.encode(), client_addr)  # Send error message to the client

def start_resolver(my_port, parent_ip, parent_port, cache_timeout):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(('', my_port))
        print(f"Resolver listening on port {my_port}...")

        while True:
            data, client_addr = server_socket.recvfrom(1024)
            domain = data.decode()
            print(f"Received query for: {domain} from {client_addr}")
            resolve(domain, parent_ip, parent_port, cache_timeout, client_addr)

if __name__ == '__main__':
    my_port = int(sys.argv[1])
    parent_ip = sys.argv[2]
    parent_port = int(sys.argv[3])
    cache_timeout = int(sys.argv[4])

    print(f"Starting resolver with the following parameters:")
    print(f"Port: {my_port}")
    print(f"Parent server: {parent_ip}:{parent_port}")
    print(f"Cache timeout: {cache_timeout} seconds")

    start_resolver(my_port, parent_ip, parent_port, cache_timeout)
