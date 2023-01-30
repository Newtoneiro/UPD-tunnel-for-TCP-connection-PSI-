#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define HOST "172.21.22.5"
#define PORT 9000

int main(int argc, char *argv[]){
  int sockfd, portno;
  char buffer[64];
  struct sockaddr_in serveraddr, clientaddr;

  if (argc < 3) {
    fprintf(stderr,"Setting default port to 9000\n");
    portno = PORT;
  }

  sockfd = socket(AF_INET, SOCK_DGRAM, 0);
  if (sockfd < 0) {
    perror("ERROR while opening socket");
    exit(1);
  }
  memset(&serveraddr, 0, sizeof(serveraddr));
  memset(&clientaddr, 0, sizeof(clientaddr));

  serveraddr.sin_family = AF_INET;
  serveraddr.sin_addr.s_addr = inet_addr(HOST);
  serveraddr.sin_port = htons(portno);

  if (bind(sockfd, (const struct sockaddr *)&serveraddr, sizeof(serveraddr)) == -1) {
    perror("BINDING ERROR");
    exit(1);
  }

  printf("C Server listening on 172.21.22.5:%d\n", portno);

  int len, n;
  len = sizeof(clientaddr);
  while (1) {
    n = recvfrom(sockfd, (char *)buffer, 64, MSG_WAITALL, ( struct sockaddr *) &clientaddr, &len);
    printf("Received %d bytes from %s:%s\n", n, inet_ntoa(clientaddr.sin_addr), buffer);
  }
  return 0;
}
