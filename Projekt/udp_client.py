import socket
import select
from helper_functions import getConfig, unpickleData, pickleData, log, xorEncrypt

LISTEN_SIZE = 5

TCP_CLIENT_CONFIRM_CONNECTION_DATA = "Connection granted [UDP client]"
TCP_CLIENT_CONFIRM_DISCONNECT_DATA = "Closed connection [UDP client]"
UDP_SERVER_REQUEST_CONNECTION_DATA = "Connection request [UDP client]"
UDP_SERVER_REQUEST_DISCONNECTION_DATA = "Close connection request [UDP client]"

TCP_SERVER_NOT_RESPONDING_DATA = "TCP server not responding [UDP client]"

def main():
    config = getConfig()

    client_ip = config["udp_client"].ip
    client_port = config["udp_client"].port

    server_ip = config["udp_server"].ip
    server_port = config["udp_server"].port

    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"===| UDP Client listening on {client_ip}:{client_port} |===")
        s.bind((client_ip, client_port))
        s.listen(LISTEN_SIZE)
        
        while True:
          client, tcpClientAddress = s.accept()
          # Connection request from TCP client
          log("Received connection request from TCP client", 1, tcpClientAddress)
          
          # Request connection to UDP server
          connectionData = pickleData(UDP_SERVER_REQUEST_CONNECTION_DATA, 0)
          log("Sending connection request to UDP server", 0, (server_ip, server_port), UDP_SERVER_REQUEST_CONNECTION_DATA)
          udp_client.sendto(connectionData, (server_ip, server_port))

          # Receive connection accept from UDP server
          rawConfirmationData, udpServerAddr = udp_client.recvfrom(config["udp_client"].buff_size)
          confirmationData = unpickleData(rawConfirmationData)
          if (confirmationData['header']['status'] == 0):
            log("Established connection with UDP server", 1, udpServerAddr, confirmationData['payload'].decode('utf-8'))
            
            # Confirm connection to TCP client
            coinfirmationData = pickleData(TCP_CLIENT_CONFIRM_CONNECTION_DATA, 0)
            client.sendall(coinfirmationData)
            log("Establishing connection with TCP client", 0, tcpClientAddress)
            connected = True
          else:
            log("Couldn't connect to TCP server", 1, udpServerAddr, confirmationData['payload'].decode('utf-8'))
            
            # Pass information to TCP client
            coinfirmationData = pickleData(TCP_SERVER_NOT_RESPONDING_DATA, 2)
            log("Sending disconnect confirmation to TCP client", 0, tcpClientAddress, TCP_SERVER_NOT_RESPONDING_DATA)
            client.sendall(coinfirmationData)

            connected = False
            client.close()
          
          with client:
            while connected:
              readable, _, _ = select.select([client], [], [], 0)
              
              if readable:
                rawDataFromTCPClient = client.recv(config['udp_client'].buff_size)
                if not rawDataFromTCPClient:
                  break
                dataFromTCPClient = unpickleData(rawDataFromTCPClient)
                if dataFromTCPClient['header']['status'] == 2:
                  
                  # Close connection with UDP server
                  rawUDPServerDisconnectData = pickleData(UDP_SERVER_REQUEST_DISCONNECTION_DATA, 2)

                  # Encrypt data
                  encryptedData = xorEncrypt(config['xorKey'], rawUDPServerDisconnectData)

                  log("Sending disconnect request to UDP server", 0, (server_ip, server_port), UDP_SERVER_REQUEST_DISCONNECTION_DATA)
                  udp_client.sendto(encryptedData, (server_ip, server_port))
                  rawConfirmationData, udpServerAddress = udp_client.recvfrom(config["udp_client"].buff_size)
                  
                  # Decrypt data
                  decryptedData = xorEncrypt(config['xorKey'], rawConfirmationData)

                  confirmationData = unpickleData(decryptedData)
                  assert(confirmationData['header']['status'] == 2)
                  log("Disconnected from UDP server", 1, udpServerAddress, confirmationData['payload'].decode('utf-8'))
                  
                  # Close connection with TCP client
                  rawCloseConnectionData = pickleData(TCP_CLIENT_CONFIRM_DISCONNECT_DATA, 2)
                  client.send(rawCloseConnectionData)
                  log("Sending disconned confirmation to TCP client", 0, tcpClientAddress, TCP_CLIENT_CONFIRM_DISCONNECT_DATA)

                  connected = False
                  break
                else:
                  # Pass message to UDP server
                  log("Passing data to UDP server", 0, (server_ip, server_port), dataFromTCPClient['payload'].decode('utf-8'))
                  rawPassDataToUDPServer = pickleData(dataFromTCPClient['payload'].decode('utf-8'), 1)
                  
                  # Encrypt data
                  encryptedData = xorEncrypt(config['xorKey'], rawPassDataToUDPServer)
                  
                  udp_client.sendto(encryptedData, (server_ip, server_port))

                  # Revceive data from UDP server
                  rawEncryptedDataFromUDPServer, udpServerAddress = udp_client.recvfrom(config["udp_client"].buff_size)
                  
                  # Decrypt data
                  rawDataFromUDPServer = xorEncrypt(config['xorKey'], rawEncryptedDataFromUDPServer)
                  
                  dataFromUDPServer = unpickleData(rawDataFromUDPServer)
                  if dataFromUDPServer['header']['status'] == 1:
                    log("Recieved data from UDP server", 1, udpServerAddress, dataFromUDPServer['payload'].decode('utf-8'))

                    # Pass message to TCP client
                    log("Passing data to TCP client", 0, tcpClientAddress, dataFromUDPServer['payload'].decode('utf-8'))
                    client.send(rawDataFromUDPServer)
                  else:
                    # TCP server is down
                    rawCloseConnectionData = pickleData(TCP_SERVER_NOT_RESPONDING_DATA, 2)
                    client.send(rawCloseConnectionData)
                    log("Sending disconned confirmation to TCP client", 0, tcpClientAddress, TCP_SERVER_NOT_RESPONDING_DATA)

                    connected = False
                    break
              
if __name__ == "__main__":
    main()

