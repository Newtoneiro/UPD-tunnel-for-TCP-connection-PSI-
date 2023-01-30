import socket as s
import random

HOST = '172.21.22.5'
PORT = 9000
BUFFER = 1024

messages = ["Hello world!", "Bazinga", "Random Data", "Top secret", "abcdef"]

print(f"Client connecting to {HOST}:{PORT}")

with s.socket(s.AF_INET, s.SOCK_STREAM) as client:
  client.connect((HOST, PORT));
  data = random.choice(messages)
  client.sendall(data.encode('utf-8'))
  data = client.recv(BUFFER)
  print(f"Data received from server: {data.decode('utf-8')}")
  client.close()

print("Client finished.")
