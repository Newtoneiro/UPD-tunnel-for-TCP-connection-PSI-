import socket as s

PORT = 9000
BUFFER = 1024
HOST = s.gethostbyname(s.gethostname())

with s.socket(s.AF_INET, s.SOCK_DGRAM) as server:
  server.bind((HOST, PORT))
  print(f"Server will run on {HOST}:{PORT}")
  while True:
    data, address = server.recvfrom(BUFFER)
    print(f"Message received from {address}: {data.decode('utf-8')}")
