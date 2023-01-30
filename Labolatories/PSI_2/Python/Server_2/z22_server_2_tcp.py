import socket as s
import select

PORT = 9000
BUFFER = 2
HOST = s.gethostbyname(s.gethostname())

with s.socket(s.AF_INET, s.SOCK_STREAM) as server:
  server.bind((HOST, PORT))
  server.listen( 5 )
  print(f"Server will run on {HOST}:{PORT}")

  while True:
    client, address = server.accept()
    client.settimeout(2.0)
    data = b''
    while True:
      part = client.recv(BUFFER)
      data += part
      if "0" in part.decode('utf-8'):
        break
    client.settimeout(None)
    print(f"Received data: {data.decode('utf-8')}")
    client.sendall("Message received.".encode('utf-8'))
    client.close()
  server.close()

