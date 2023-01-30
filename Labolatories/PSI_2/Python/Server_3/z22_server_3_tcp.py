import socket as s
from socket import *

PORT = 9000
BUFFER = 1024
HOST = s.gethostbyname(s.gethostname())
TIMEOUT_TIME = 1

with s.socket(s.AF_INET, s.SOCK_STREAM) as server:
  server.bind((HOST, PORT))
  server.listen( 5 )
  print(f"Server will run on {HOST}:{PORT}")
  while True:
    client, address = server.accept()
    with client:
      try:
        client.settimeout(TIMEOUT_TIME)
        data = client.recv(BUFFER)
      except timeout:
        print("Couldn't recveive data (TIMEOUT)")
      if not data:
        break
      print(f"Message received from client: {data.decode('utf-8')}")
      client.sendall("Message received.\0".encode('utf-8'))
    client.close()
  server.close()

