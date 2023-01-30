#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define PORT 9000
#define READ_SIZE 5

int main(int argc, char *argv[]){
  int sockfd, connfd, portno;
  char buffer[READ_SIZE];
  char messbuffer[1024];
  struct sockaddr_in serveraddr, clientaddr;

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
  memset(&clientaddr, 0, sizeof(clientaddr));

  serveraddr.sin_family = AF_INET;
  serveraddr.sin_addr.s_addr = INADDR_ANY;
  serveraddr.sin_port = htons(portno);

  if (bind(sockfd, (const struct sockaddr *)&serveraddr, sizeof(serveraddr)) == -1) {
    perror("BINDING ERROR");
    exit(1);
  }

  if ((listen(sockfd, 5)) != 0) {
    perror("ERROR LISTENING");
    exit(1);
  }

  printf("C Server listening on 172.21.22.5:%d\n", portno);

  int len, n, rval;
  len = sizeof(clientaddr);
  while (1) {
    connfd = accept(sockfd, (struct sockaddr *) &clientaddr, &len);
    if (connfd > 0) {
      printf("Connection from %s\n", inet_ntoa(clientaddr.sin_addr));

      do {
        // Clear buffer to prevent overflow
        memset(buffer, 0, sizeof buffer);
        if ((rval = read(connfd, buffer, sizeof buffer)) == -1){
          perror("ERROR recieving data");
          exit(1);
        }
        if (rval > 0){
          printf("> %d : %s\n", rval, buffer);
        }
      } while (!(rval < READ_SIZE));

      memset(&messbuffer, 0, sizeof(messbuffer));
      strcpy(messbuffer, "Message received.");
      if (send(connfd, messbuffer, strlen(messbuffer), 0) < 0){
        perror("ERROR sending data");
        exit(1);
      }
    }
    close(connfd);
  }
  close(sockfd);
  return 0;
}
