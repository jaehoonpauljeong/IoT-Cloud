/* echo client*/
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

int  main(int argc, char *argv[])
{	int  s;
 	struct  sockaddr_in  sin;
	char  msg[80] = "Hello World!";
	int  n;

	if (argc < 3) { printf("%s ip-address port\n", argv[0]); return -1; }

	if ((s = socket(PF_INET, SOCK_STREAM, 0)) < 0) {
		perror("socket() error"); return -1;
	}

	sin.sin_family = AF_INET;
	sin.sin_port = htons(atoi(argv[2]));
	sin.sin_addr.s_addr = inet_addr(argv[1]);

	if (connect(s, (struct sockaddr *)&sin, sizeof(sin)) < 0) {
		perror("connect() error"); return -1;
	}
	if (write(s, msg, strlen(msg)+1) < 0) {
		perror("write() error"); return -1;
	}
	if ((n = read(s, msg, sizeof(msg))) < 0) {
		perror("read() error"); return -1;
	}
	printf("%d bytes: %s\n", n, msg);
	if (close(s) < 0) { perror("close() error"); return -1; }
	return 0;
}
