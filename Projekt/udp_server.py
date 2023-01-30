import socket
import select
from helper_functions import getConfig, pickleData, unpickleData, log, xorEncrypt

UDP_CLIENT_CONFIRM_CONNECTION_DATA = "Connection granted [UDP server]"
UDP_CLIENT_CONFIRM_DISCONNECT_DATA = "Closed connection [UDP server]"
TCP_SERVER_REQUEST_CONNECTION_DATA = "Connection request [UDP server]"
TCP_SERVER_REQUEST_DISCONNECTION_DATA = "Close connection request [UDP server]"

TCP_SERVER_NOT_RESPONDING_DATA = "TCP server not responding [UDP server]"

def main():
  config = getConfig()

  udp_server_ip = config["udp_server"].ip
  udp_server_port = config["udp_server"].port

  tcp_server_ip = config["tcp_server"].ip
  tcp_server_port = config["tcp_server"].port

  connected = False

  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_server:
    udp_server.bind((udp_server_ip, udp_server_port))
    print(f"===| UDP Server listennig on: {udp_server_ip}:{udp_server_port} |===")

    while True:
      # Connection request from UDP client
      rawConnectionData, udpClientAddress = udp_server.recvfrom(config["udp_server"].buff_size)
      connectionData = unpickleData(rawConnectionData)
      assert(connectionData['header']['status'] == 0)
      log("Received connection request from UDP client", 1, udpClientAddress, connectionData['payload'].decode('utf-8'))
      
      # Connection request to TCP server
      log("Sending connection request to TCP server", 0, (tcp_server_ip, tcp_server_port))
      tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      try:
        tcp_server.connect((tcp_server_ip, tcp_server_port))

        # Receive connection accept from TCP server
        rawConfirmationData = tcp_server.recv(config['tcp_server'].buff_size)
        confirmationData = unpickleData(rawConfirmationData)
        assert(confirmationData['header']['status'] == 0)
        log("Established connection with TCP server", 1, (tcp_server_ip, tcp_server_port), confirmationData['payload'].decode('utf-8'))
        
        # Confirm connection to UDP client
        rawConfirmationData = pickleData(UDP_CLIENT_CONFIRM_CONNECTION_DATA, 0)
        udp_server.sendto(rawConfirmationData, udpClientAddress)
        log("Establishing connection with UDP client", 0, udpClientAddress, UDP_CLIENT_CONFIRM_CONNECTION_DATA)
        connected = True
      except Exception as e:
        # Can't connect to TCP server
        log(f"Error: {e}", 1, (tcp_server_ip, tcp_server_port), TCP_SERVER_NOT_RESPONDING_DATA)
        rawCloseConnectionData = pickleData(TCP_SERVER_NOT_RESPONDING_DATA, 2)
        log("Sending disconnect confirmation to UDP client", 0, udpClientAddress, TCP_SERVER_NOT_RESPONDING_DATA)
        udp_server.sendto(rawCloseConnectionData, udpClientAddress)
        connected = False

      while connected:
        readable, _, _ = select.select([udp_server], [], [], 0)
        if readable:
          rawDataFromUDPClient, udpClientAddress = udp_server.recvfrom(config["udp_server"].buff_size)
          if not rawDataFromUDPClient:
            break
          # Decrypt data
          decryptedDataFromUDPClient = xorEncrypt(config['xorKey'], rawDataFromUDPClient)
          
          dataFromUDPClient = unpickleData(decryptedDataFromUDPClient)
          if dataFromUDPClient['header']['status'] == 2:
            # Close connection with TCP server
            rawTCPServerDisconnectData = pickleData(TCP_SERVER_REQUEST_DISCONNECTION_DATA, 2)
            log("Sending disconnect request to TCP server", 0, (tcp_server_ip, tcp_server_port), TCP_SERVER_REQUEST_DISCONNECTION_DATA)
            tcp_server.sendall(rawTCPServerDisconnectData)
            rawConfirmationData = tcp_server.recv(config["udp_server"].buff_size)
            confirmationData = unpickleData(rawConfirmationData)
            assert(confirmationData['header']['status'] == 2)
            tcp_server.close()
            log("Disconnected from TCP server", 1, (tcp_server_ip, tcp_server_port), confirmationData['payload'].decode('utf-8'))
            
            # Close connection with UDP client
            rawCloseConnectionData = pickleData(UDP_CLIENT_CONFIRM_DISCONNECT_DATA, 2)
            
            # Encrypt data
            encryptedData = xorEncrypt(config['xorKey'], rawCloseConnectionData)
            
            udp_server.sendto(encryptedData, udpClientAddress)
            log("Sending disconned confirmation to UDP client", 0, udpClientAddress, UDP_CLIENT_CONFIRM_DISCONNECT_DATA)
            connected = False
            break
          else:
            # Pass message to TCP server
            log("Passing data to TCP server", 0, (tcp_server_ip, tcp_server_port), dataFromUDPClient['payload'].decode('utf-8'))
            rawDataToTCPServer = pickleData(dataFromUDPClient['payload'].decode('utf-8'), 1)
            tcp_server.sendall(rawDataToTCPServer)

            # Recieve data from TCP server
            retry = 0
            rawDataFromTCPServer = b''
            while retry < 3 and len(rawDataFromTCPServer) == 0:
              rawDataFromTCPServer = tcp_server.recv(config['tcp_server'].buff_size)
              retry += 1
            if rawDataFromTCPServer:
              # Server is responding
              dataFromTcpServer = unpickleData(rawDataFromTCPServer)
              log("Received data from TCP server", 1, (tcp_server_ip, tcp_server_port), dataFromTcpServer['payload'].decode('utf-8'))
              
              # Pass message to UDP client
              encryptedRawDataFromTCPServer = xorEncrypt(config['xorKey'], rawDataFromTCPServer)
              log("Sending data to UDP client", 0, udpClientAddress, dataFromTcpServer['payload'].decode('utf-8'))
              udp_server.sendto(encryptedRawDataFromTCPServer, udpClientAddress)
            else:
              # Server is down
              log("=! TCP server is down !=", 1, (tcp_server_ip, tcp_server_port))
              # Close connection with UDP client
              rawCloseConnectionData = pickleData(TCP_SERVER_NOT_RESPONDING_DATA, 2)
              
              # Encrypt data
              encryptedData = xorEncrypt(config['xorKey'], rawCloseConnectionData)
              
              udp_server.sendto(encryptedData, udpClientAddress)
              log("Sending disconned confirmation to UDP client", 0, udpClientAddress, TCP_SERVER_NOT_RESPONDING_DATA)
              connected = False
              break

if __name__ == "__main__":
    main()
