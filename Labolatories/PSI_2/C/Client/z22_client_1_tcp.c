#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define DATA "Message sent from c client"
#define HOST "172.21.22.5"
#define PORT 9000

int main(int argc, char *argv[]){
  int sockfd, portno;
  char buffer[1024];
  struct sockaddr_in serveraddr;

  if (argc < 3) {
      fprintf(stderr,"Setting default port to 9000\n");
      portno = PORT;
  }

  sockfd = socket(AF_INET, SOCK_STREAM, 0);
  if (sockfd < 0) {
        perror("ERROR while opening socket");
        exit(1);
  }
  memset(&serveraddr, 0, sizeof(serveraddr));

  serveraddr.sin_family = AF_INET;
  serveraddr.sin_addr.s_addr = inet_addr(HOST);
  serveraddr.sin_port = htons(portno);

  if (connect(sockfd, (struct sockaddr *)&serveraddr, sizeof(serveraddr)) < 0){
    perror("ERROR connecting to socket");
    exit(1);
  }

  strncpy(buffer, DATA, sizeof(DATA));

  if (send(sockfd, buffer, strlen(buffer), 0) < 0){
    perror("ERROR sending data");
    exit(1);
  }
  // Fill buffer with nulls to prevent buffer overflow
  memset(&buffer, 0 , sizeof(buffer));

  if (recv(sockfd, buffer, sizeof(buffer), 0) < 0){
    perror("ERROR recieving data");
    exit(1);
  }

  printf("Message received from server: %s\n", buffer);

  close(sockfd);

  return 0;
}
