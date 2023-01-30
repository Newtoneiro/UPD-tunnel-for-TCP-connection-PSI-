#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define DATA "struct { uint32_t a; int16_t b; char c[10];}"
#define HOST "172.21.22.5"
#define PORT 9000

int main(int argc, char *argv[]){
  int sockfd, portno;
  char buffer[64];
  struct sockaddr_in serveraddr;
  
  const int threeLen=sizeof(DATA);
  struct DataStruct {
    uint32_t a;
    int16_t b;
    char c[10];
  };

  struct DataStruct concreteData;
  concreteData.a = 12345;
  concreteData.b = 12345;
  strcpy(concreteData.c, DATA);

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

  sendto(sockfd, &concreteData, sizeof(struct DataStruct),
    MSG_CONFIRM, (const struct sockaddr *) &serveraddr,
      sizeof(serveraddr));

  printf("Messege sent.\n");
  return 0;
}
