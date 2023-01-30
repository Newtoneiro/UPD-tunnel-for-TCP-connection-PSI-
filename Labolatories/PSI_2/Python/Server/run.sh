#!/bin/bash

docker run -it --rm --network-alias z22_server_1_tcp_py --network z22_network --name z22_server_1_tcp_py --ip 172.21.22.5 z22_server_1_tcp_py
