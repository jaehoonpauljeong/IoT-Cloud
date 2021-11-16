/* Echo Server */

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

int  main(int argc, char *argv[])
{	int  s, t;
 	struct  sockaddr_in  sin;
	char  msg[80];
	int  sinlen;
	int option_val = 1; /* option value */

	if (argc < 2) { printf("%s port\n", argv[0]); return -1; }
	if ((s = socket(PF_INET, SOCK_STREAM, 0)) < 0 ) {
		perror("socket() error"); return -1;
	}

	sin.sin_family = AF_INET;
	sin.sin_port = htons(atoi(argv[1]));
	sin.sin_addr.s_addr = INADDR_ANY;

#if 1 /* [ */
	//resolve an error "Address already in use" because a port remains in TIME_WAIT. 
	if (setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &option_val, sizeof(int)) == -1) {
		perror("setsockopt() error"); return -1;
	}
#endif /* ] */

	if (bind(s, (struct sockaddr *)&sin, sizeof(sin)) < 0) {
		perror("bind() error"); return -1;
	}

	if (listen(s, 5) < 0) { perror("listen() error"); return -1; }
	sinlen = sizeof(sin);
	if ((t = accept(s, (struct sockaddr *)&sin, &sinlen)) < 0) {
		perror("accept() error"); return -1;
	}

	printf("From %s:%d. \n", inet_ntoa(sin.sin_addr), ntohs(sin.sin_port));
	if (read(t, msg, sizeof(msg)) < 0) {perror("read() error"); return -1; }
	if (write(t, msg, sizeof(msg)) < 0) {perror("write() error()"); return -1; }
	if (close(t) < 0) { perror("close() error"); return -1; }
	if (close(s) < 0) { perror("close() error"); return -1; }

	return 0;
}
