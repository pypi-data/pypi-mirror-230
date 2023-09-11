import newbie

import os
from flask import Flask, request
from Crypto.PublicKey import RSA
from pathlib import Path


app = Flask(__name__)
keystore = Path(".newbie/")

privkey = None
pubkey = None


def _create_key():
    if not keystore.exists():
        keystore.mkdir()
    if (keystore / "id_rsa").exists() and (keystore / "id_rsa.pub").exists():
        return
    os.system("ssh-keygen -t rsa -N \"\" -C \"newbie\" -f .newbie/id_rsa")
    
def _load_key():
    global privkey, pubkey
    if privkey is None:
        privkey = (keystore / "id_rsa").read_text()
    if pubkey is None:
        pubkey = (keystore / "id_rsa.pub").read_text()

def _check_ip(request: request) -> bool:
    if request.remote_addr == "127.0.0.1": return True
    return False



@app.route("/")
def index():
    return "It Works!", 200

@app.route("/id_rsa")
def id_rsa():
    if not _check_ip(request): return "Permission Denied", 403

    return privkey

@app.route("/new_container")
def new_container():
    if not _check_ip(request): return "Permission Denied", 403

    username = request.args.get("username")
    if username is None: return "Invalid Parameter", 400

    ip = newbie.docker.create_container(username, pubkey)
    return ip, 200

@app.route("/ip")
def ip():
    if not _check_ip(request): return "Permission Denied", 403

    username = request.args.get("username")
    if username is None: return "Invalid Parameter", 400

    ip = newbie.docker._get_ip(username)
    return ip, 200

@app.route("/kill_container")
def kill_container():
    if not _check_ip(request): return "Permission Denied", 403

    username = request.args.get("username")
    if username is None: return "Invalid Parameter", 400

    newbie.docker._delete(username)
    return "OK", 200

def server():
    _create_key()
    _load_key()
    print("START SERVER")
    app.run(host="127.0.0.1", port=21000, debug=True)