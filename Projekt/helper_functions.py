import json
import os
import pickle

FILENAME = "config.json"

dirPath = os.path.dirname(__file__)
filePath = os.path.join(dirPath, FILENAME)

class ServerData:
    def __init__(self, ip, port, buff_size):
        self.ip = ip
        self.port = port
        self.buff_size = buff_size

def getConfig():
    with open(filePath, "r") as f:
        data = json.load(f)
        udp_client = ServerData(data["client"]["ip"], data["client"]["port"], data["client"]["buffer_size"])
        udp_server = ServerData(data["server"]["ip"], data["server"]["port"], data["server"]["buffer_size"])
        tcp_server = ServerData(data["tcp_server"]["ip"], data["tcp_server"]["port"], data["tcp_server"]["buffer_size"])
        xorKey = data["xor_key"]

        return {
            'udp_client': udp_client,
            'udp_server': udp_server,
            'tcp_server': tcp_server,
            'xorKey': xorKey
        }

def pickleData(message: str, status: int) -> bytes:
    data = {
        'header': {
            'status': status,
            'len': len(message)
        },
        'payload': message.encode('utf-8')
    }
    pickled_data = pickle.dumps(data)
    return pickled_data

def unpickleData(data: bytes) -> bytes:
    unpickledData = pickle.loads(data)
    return unpickledData

def log(action: int, dir: int, addr: str, message:str ="") -> None:
    direction = "-->"
    if (dir == 1):
        direction = "<--"
    formatted_addr = f"{direction}{addr[0]}:{addr[1]}"
    formatted_message = f"[{len(message)}]{message}"
    if len(message) == 0:
        formatted_message = "---"
    print(f"{action:<50} | {formatted_addr:<20} | {formatted_message:<50}")

def xorEncrypt(key: str, message: bytes) -> bytes:
    key = key.encode()

    encrypted_message = b''
    for i, b in enumerate(message):
        encrypted_message += bytes([b ^ key[i % len(key)]])

    return encrypted_message


