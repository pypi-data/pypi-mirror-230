import newbie

import os
from requests import get
from pathlib import Path
import socket

input = newbie.input
print = newbie.print
server_url = "http://127.0.0.1:21000/"
keyPath = Path(".newbie/newbie_id_rsa")

def _check_key():
    if not keyPath.parent.exists():
        keyPath.parent.mkdir()
        os.system(f"chmod 700 {keyPath.parent}")
    if not keyPath.exists():
        id_rsa = get(server_url + "id_rsa").text
        keyPath.write_text(id_rsa)
        os.system(f"chmod 600 {keyPath}")


def client():
    try:
        if get(server_url).status_code != 200:
            print("Sorry, Server is not running in this host.")
            exit(1)
    except:
        print("Sorry, Server is not running in this host.")
        exit(1)
    username = input("Insert your Username: ")
    username = username.replace(" ", "")
    if username == "":
        print("Invalid Username")
        exit(1)

    print("Creating new newbie container...")
    ip = get(server_url + "new_container?username=" + username).text
    print(f"Newbie container created. Connecting to {username}'s container...")

    _check_key()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while s.connect_ex((ip, 22)) != 0:
        pass
    s.close()
    
    os.system(f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i {keyPath} {username}@{ip}")