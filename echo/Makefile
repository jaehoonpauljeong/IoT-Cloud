CC = gcc
FLAG1 = -o $@
FLAG2 = -o $@ -g

all: echo-client echo-server

echo-client: echo-client.c
	$(CC) $(FLAG1) echo-client.c

echo-server: echo-server.c
	$(CC) $(FLAG1) echo-server.c

all.db: echo-client.db echo-server.db

echo-client.db: echo-client.c
	$(CC) $(FLAG2) echo-client.c

echo-server.db: echo-server.c
	$(CC) $(FLAG2) echo-server.c

clean:
	rm -f *.o *.do echo-client echo-server *.db
