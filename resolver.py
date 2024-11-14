import socket
import sys
import time

cache = {}
cache_time = {}
cache_timeout = 0

def inCache(domain):
    if domain in cache:
        print(f"Domain {domain} found in cache. Checking cache validity...")
        if time.time() - cache_time[domain] < cache_timeout:
            print(f"Cache is valid. Returning cached response: {cache[domain]}")
            return True
        else:
            print(f"Cache expired for domain {domain}. Querying parent server.")
            return False
    return False

def resolve(domain, parent_ip, parent_port, client_addr, sock):
    print(f"Attempting to resolve domain: {domain}")
    
    if inCache(domain):
        response = cache[domain]
        print(f"Cache is valid. Returning cached response: {response}")
        sock.sendto(response.encode(), client_addr)
        return
    
    print(f"Domain {domain} not in cache or cache expired. Querying parent server...")
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as parent_sock:
        parent_sock.sendto(domain.encode(), (parent_ip, parent_port))
        parent_sock.settimeout(2)

        try:
            print(f"Sent query to {parent_ip}:{parent_port}")
            data, _ = parent_sock.recvfrom(1024)
            response = data.decode()
            print(f"Received response from parent server: {response}")

            cache[domain] = response.split(",")[1]
            cache_time[domain] = time.time()

            print(f"Cached response for {domain}: {response}")

            if response.endswith('NS'):
                ns_info = response.split(",")
                ns_ip, ns_domain = ns_info[1].split(":")
                print(f"Response is a referral. Resolving nameserver {ns_domain}...")
                resolve(ns_domain, ns_ip, ns_domain, client_addr, sock)
            else:
                sock.sendto(response.encode(), client_addr)

        except socket.timeout:
            error_message = "non-existent domain"
            print(f"Error: {error_message} (timeout)")
            sock.sendto(error_message.encode(), client_addr)

def main():
    global cache_timeout
    my_port = int(sys.argv[1])
    parent_ip = sys.argv[2]
    parent_port = int(sys.argv[3])
    cache_timeout = int(sys.argv[4])

    print(f"Starting resolver with Port: {my_port}, Parent IP: {parent_ip}, Parent Port: {parent_port}, Cache Timeout: {cache_timeout}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('', my_port))

        print(f"Resolver listening on port {my_port}...")

        while True:
            data, client_addr = s.recvfrom(1024)
            domain = data.decode()
            print(f"Received query for: {domain} from {client_addr}")
            resolve(domain, parent_ip, parent_port, client_addr, s)

if __name__ == '__main__':
    main()
