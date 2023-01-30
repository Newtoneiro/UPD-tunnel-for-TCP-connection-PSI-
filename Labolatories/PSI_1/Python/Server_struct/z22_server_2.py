import socket as s
import struct

PORT = 9000
BUFFER = 2048
HOST = s.gethostbyname(s.gethostname())

with s.socket(s.AF_INET, s.SOCK_DGRAM) as server:
  server.bind((HOST, PORT))
  print(f"Server will run on {HOST}:{PORT}")

  data = server.recv(BUFFER)
  print(f"Received Struct: {data}")
  print(len(data))
  my_struct = struct.unpack('II8s', data)
  print(my_struct)
