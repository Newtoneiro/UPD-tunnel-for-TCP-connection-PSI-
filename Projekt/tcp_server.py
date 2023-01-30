import socket
import select
from helper_functions import getConfig, pickleData, unpickleData, log

LISTEN_SIZE = 5
SERVER_RESPONSE_MESSAGE = "Message Received [TCP server]"

TCP_CLIENT_CONFIRM_CONNECTION_DATA = "Connection granted [TCP server]"
UDP_SERVER_CONFIRM_DISCONNECT_DATA = "Closed connection [TCP server]"

def main():
  config = getConfig()

  server_ip = config["tcp_server"].ip
  server_port = config["tcp_server"].port

  connected = False

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_server:
    print(f"===| TCP Server listennig on: {server_ip}:{server_port} |===")
    tcp_server.bind((server_ip, server_port))
    tcp_server.listen(LISTEN_SIZE)

    while True:
      # Connect to UDP server
      client, udpClientAddress = tcp_server.accept()
      log("Received connection request from UDP server", 1, udpClientAddress)
      rawConfirmationData = pickleData(TCP_CLIENT_CONFIRM_CONNECTION_DATA, 0)
      client.sendall(rawConfirmationData)
      log("Established connection with UDP server", 0, udpClientAddress, TCP_CLIENT_CONFIRM_CONNECTION_DATA)
      connected = True

      while connected:
        readable, _, _ = select.select([client], [], [], 0)
        
        if readable:
          rawDataFromUDPServer = client.recv(config['tcp_server'].buff_size)
          if not rawDataFromUDPServer:
            break
          dataFromUDPServer = unpickleData(rawDataFromUDPServer)
          if dataFromUDPServer['header']['status'] == 2:
            # Close connection with udp_server
            rawDataEndConnection = pickleData(UDP_SERVER_CONFIRM_DISCONNECT_DATA, 2)
            client.send(rawDataEndConnection)
            log("TCP client disconnected", 1, udpClientAddress, UDP_SERVER_CONFIRM_DISCONNECT_DATA)

            connected = False
            break
          else:
            log("Data received from UDP server", 1, udpClientAddress, dataFromUDPServer['payload'].decode('utf-8'))
            rawDataFromUDPServer = pickleData(SERVER_RESPONSE_MESSAGE, 1)
            log("Sending data to UDP server", 0, udpClientAddress, SERVER_RESPONSE_MESSAGE)
            client.sendall(rawDataFromUDPServer)

if __name__ == "__main__":
  main()
