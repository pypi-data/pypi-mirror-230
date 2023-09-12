import newbie

import os
import time

input = newbie.input
print = newbie.print

def _system(command: str) -> int:
    print("[+] " + command)
    return os.system(command)

def container():
    AUTHORIZED_KEYS = os.environ.get("NEWBIE_AUTHORIZED_KEYS")
    if AUTHORIZED_KEYS is None:
        print("Please set NEWBIE_AUTHORIZED_KEYS environment variable.")
        exit(1)
    
    USERNAME = os.environ.get("NEWBIE_USERNAME")
    if USERNAME is None:
        print("Please set NEWBIE_USERNAME environment variable.")
        exit(1)
    
    _system(f"useradd -m -s /bin/bash -G sudo -u 1000 {USERNAME}")
    _system(f"echo \"{USERNAME} ALL=(ALL:ALL) NOPASSWD:ALL\" >> /etc/sudoers")

    _system(f"su - -c 'mkdir -p ~/.ssh && echo \"{AUTHORIZED_KEYS}\" > ~/.ssh/authorized_keys' {USERNAME}")
    _system(f"su - -c 'chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys' {USERNAME}")

    _system(f"service ssh start")

    nowtime = time.time()
    while True:
        connect = False
        if _system("ss -t | grep -q ssh") == 0:
            nowtime = time.time()
            connect = True

        if not connect: 
            if time.time() - nowtime > 60:
                exit()
            print("Exit for time: " + str(60 - int(time.time() - nowtime)))
        time.sleep(2)
            
