import socket as s

PORT = 9000
BUFFER = 1024
HOST = s.gethostbyname(s.gethostname())

with s.socket(s.AF_INET, s.SOCK_STREAM) as server:
  server.bind((HOST, PORT))
  server.listen( 5 )
  print(f"Server will run on {HOST}:{PORT}")
  while True:
    client, address = server.accept()
    with client:
      data = client.recv(BUFFER)
      if not data:
        break
      print(f"Message received from client: {data.decode('utf-8')}")
      client.sendall("Message received.\0".encode('utf-8'))
    client.close()
  server.close()

