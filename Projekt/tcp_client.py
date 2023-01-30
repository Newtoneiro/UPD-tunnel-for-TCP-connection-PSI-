import socket
import select
from helper_functions import getConfig, pickleData, unpickleData, log

def main():
    config = getConfig()

    server_ip = config["udp_client"].ip
    server_port = config["udp_client"].port
    
    connected = False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_client:

        # Conecting to udp client
        log("Sending connection request to UDP client", 0, (server_ip, server_port))
        tcp_client.connect((server_ip, server_port))
        rawConfirmationData = tcp_client.recv(config['udp_client'].buff_size)
        confirmationData = unpickleData(rawConfirmationData)
        if confirmationData['header']['status'] == 0:
            log("Connected to UDP client", 1, (server_ip, server_port), confirmationData['payload'].decode('utf-8'))
            connected = True
        else:
            log("Failed to connect to UDP client", 1, (server_ip, server_port), confirmationData['payload'].decode('utf-8'))
            connected = False
        
        while connected:
            _, writable, _ = select.select([], [tcp_client], [])
            if writable:
                message = input('==> Enter message: ')
                status = 1
                if message == "STOP":
                    status = 2
                # Send message to UDP client
                rawDataToUDPClient = pickleData(message, status)
                tcp_client.sendall(rawDataToUDPClient)
                
                # Receive message from UDP client
                rawDataFromUDPClient = tcp_client.recv(config['udp_client'].buff_size)
                dataFromUDPClient = unpickleData(rawDataFromUDPClient)
                if dataFromUDPClient['header']['status'] == 2:
                    log("Connection Ended", 1, (server_ip, server_port), dataFromUDPClient['payload'].decode('utf-8'))
                    connected = False
                    break
                log("Data received: ", 1, (server_ip, server_port), dataFromUDPClient['payload'].decode('utf-8'))

        tcp_client.close()

if __name__ == "__main__":
    main()

