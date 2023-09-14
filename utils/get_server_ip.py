import os, re

regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"

def fetch_server_ip():
    if not os.path.isfile('server_ip.txt'):
        with open('server_ip.txt', 'w+') as f:
            f.close()
    with open('server_ip.txt', 'r') as f:
        server_ip = f.read().rstrip()
    if(re.search(regex, server_ip)):
        print("Valid IP address")
    else:
        while True:
            server_ip = input("Enter Server IP Address: ")
            if(re.search(regex, server_ip)):
                print("Valid IP address")
                break
            else:
                print("Invalid IP address")
                continue
    with open('server_ip.txt', 'w') as f:
        f.write(server_ip)
    print(f'Server IP: {server_ip}')
    return server_ip