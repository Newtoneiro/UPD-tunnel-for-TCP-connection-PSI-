#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <arpa/inet.h>
#include <sys/un.h>

#define PORT 9000
#define TIMEOUT_TIME 10

#define MAX_READ_LEN 20
#define MAX_FDS 5

int main(int argc, char **argv) {
    int sockfd, msgsock, client_len, rval, portno;
    char* buffer[1024];
    int nfds, nactive, socktab[MAX_FDS];
    fd_set ready;
    int len;
    struct sockaddr_in serveraddr, clientaddr;
    struct timeval timeout;
    int childpid;
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

    if (bind(sockfd, (struct sockaddr *)&serveraddr, sizeof serveraddr) == -1){
      perror("BINDING ERROR");
      exit(1);
    }
    if (listen(sockfd, 5) != 0){
      perror("ERROR LISTENING");
      exit(1);
    }

    printf("C Server listening on 172.21.22.5:%d\n", portno);

    int i;
    while (1)
    {
      FD_ZERO(&ready);
      FD_SET(sockfd, &ready);
      for (i = 0; i < MAX_FDS; ++i) {
        if (socktab[i] > 0)
          FD_SET(socktab[i], &ready);
      }
      timeout.tv_sec = TIMEOUT_TIME;
      timeout.tv_usec = 0;

      if ((nactive = select(nfds, &ready, NULL, NULL, &timeout)) < -1) {
        perror("ERROR with select");
        continue;
      }

      if (FD_ISSET(sockfd, &ready)) {
        len = sizeof(clientaddr);
        msgsock = accept(sockfd, (struct sockaddr *)&clientaddr, &len);
        if ((childpid = fork()) == 0) {
          close(sockfd);
          memset(&buffer, 0, sizeof(buffer));
          printf("Message From TCP client: ");
          read(msgsock, buffer, sizeof(buffer));
          printf("%s\n", buffer);
          exit(0);
        }
        close(msgsock);
      }
      if (nactive == 0)
          printf("Timeout");
    }

    if (close(sockfd) < 0) {
        perror("ERROR closing socket");
        exit(1);
    }

    return 0;
}
