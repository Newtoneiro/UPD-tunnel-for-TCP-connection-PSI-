import socket as s
import random

HOST = '172.21.22.5'
PORT = 9000
BUFFER = 1024

messages = ["Hello world!0", "Bazinga0", "Random Data0", "Top secret0", "abcdef0"]

print(f"Client connecting to {HOST}:{PORT}")

with s.socket(s.AF_INET, s.SOCK_STREAM) as client:
  client.connect((HOST, PORT));
  data = random.choice(messages)

  client.send(data.encode('utf-8'))
  data = client.recv(BUFFER)
  print(f"Data received from server: {data.decode('utf-8')}")
  client.close()

print("Client finished.")
