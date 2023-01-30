#!/bin/bash

docker run -it --rm --network-alias z22_server_2_tcp_c --network z22_network --name z22_server_2_tcp_c --ip 172.21.22.5 z22_server_2_tcp_c
