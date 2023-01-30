import socket as s
import random

HOST = '172.21.22.5'
PORT = 9000
BUFFER = 1024

messages = ["Hello world!", "Bazinga", "Random Data", "Top secret", "abcdef"]

print(f"Client connecting to {HOST}:{PORT}")

with s.socket(s.AF_INET, s.SOCK_DGRAM) as client:
  for i in range(3):
    data = random.choice(messages)
    client.sendto(data.encode('utf-8'), (HOST, PORT))

  client.close()

print("Client finished.")
