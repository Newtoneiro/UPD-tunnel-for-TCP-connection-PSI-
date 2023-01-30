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
  char buffer[64];
  struct sockaddr_in serveraddr;

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

  serveraddr.sin_family = AF_INET;
  serveraddr.sin_addr.s_addr = inet_addr(HOST);
  serveraddr.sin_port = htons(portno);
  
  int i = 0;
  for(i = 0; i < 3; ++i) {
    sendto(sockfd, (const char *)DATA, strlen(DATA), 
      MSG_CONFIRM, (const struct sockaddr *) &serveraddr,  
        sizeof(serveraddr)); 
    printf("Messege sent.\n");
  }
  return 0;
}
