/*
1. Send NI Query in certain interval
2. When NI Reply is received nsupdate
*/

#include "ni_common.h"

static unsigned char sendbuf[BUFSIZE];
static unsigned char recvbuf[BUFSIZE];
static char temp_str_buf[256];
static char debug[64];
static char ipAddr[64];
static unsigned char ip1[SIZE_IPADDRESS_BINARY];
static unsigned char ip2[SIZE_IPADDRESS_BINARY];
static char dnsna[256];
static char dnsna_sala[256];
static char text_buf[256];
static char dnsna_list[] = "dnsna_list.txt";
static int isConflict;

int main(){
  struct sockaddr_in6 from;
  memset(sendbuf, 0x00, BUFSIZE);
  memset(recvbuf, 0x00, BUFSIZE);
  int sendlen;
  int recvlen;
  int fromlen;

  //allnode
  struct sockaddr_in6 addr;
  memset(&addr, 0, sizeof(struct sockaddr_in6));
  addr.sin6_family = AF_INET6;
  inet_pton(AF_INET6, IPV6_LINKLOCAL_ALLNODE, &addr.sin6_addr);
  inet_ntop(AF_INET6, addr.sin6_addr.s6_addr, debug, SIZE_IPADDRESS_TEXT);
  printf("addr.sin6_addr: %s\n\n", debug);

  time_t cur_time, old_time;

  int gate_socket;
  if((gate_socket = socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6)) < 0){
    perror("socket error");
    return -1;
  }
  setsockopt(gate_socket, SOL_SOCKET, SO_BINDTODEVICE, INTERFACE, strlen(INTERFACE));

  //create ni Query
  struct icmp6_nodeinfo *icmp6_query;
  icmp6_query = (struct icmp6_nodeinfo *)sendbuf;
  icmp6_query -> ni_type = ICMP6_NI_QUERY;
  icmp6_query -> ni_code = NI_QUERY_CODE_IPV6;
  icmp6_query -> ni_qtype = htons(NI_QTYPE_NODENAME);
  icmp6_query -> ni_flags = 0;
  sprintf(temp_str_buf, "%x%x%x%x%x", rand(), rand(), rand(), rand(), rand());
  for(int i = 0; i < 8; i++){
    icmp6_query -> ni_nonce[i] = temp_str_buf[i] ^ temp_str_buf[i];
    icmp6_query -> ni_nonce[i] += temp_str_buf[i * 2];
  }
  sendlen = sizeof(struct icmp6_nodeinfo);
  memcpy(&sendbuf[sendlen], &addr.sin6_addr, SIZE_IPADDRESS_BINARY);
  sendlen += SIZE_IPADDRESS_BINARY;

  if(sendto(gate_socket, sendbuf, sendlen, 0, (struct sockaddr *)&addr, sizeof(addr)) < 0){
    perror("sendto error");
    close(gate_socket);
    return -1;
  }

  for(int i = 0; i < sendlen; i++){
    printf("%02x ", sendbuf[i]);
  }
  printf("\nsendlen: %d\n", sendlen);

  printf("Sent\n");


  //listen for icmp ni reply
  while(1){
    fd_set select_fds;
    struct timeval tv;
    tv.tv_sec = 1;
    tv.tv_usec = 0;
    FD_ZERO(&select_fds);
    FD_SET(gate_socket, &select_fds);

    if(select((gate_socket + 1), &select_fds, NULL, NULL, (struct timeval *)&tv) <= 0){
      continue;
    }
    if(FD_ISSET(gate_socket, &select_fds)){
      recvlen = recvfrom(gate_socket, recvbuf, sizeof(recvbuf), 0, (struct sockaddr*)&from, &fromlen);
      if(recvbuf[0] == ICMP6_NI_REPLY){
	      for(int i = 0; i < recvlen; i++){
	        printf("%02x ",recvbuf[i]); 
        }	  
  	    printf("\nReceivelen = %d\n", recvlen);
        printf("Received icmp Reply !!!\n");
        struct icmp6_nodeinfo *msg;
        msg = (struct icmp6_nodeinfo *)recvbuf;
        int msglen;
        msglen = sizeof(struct icmp6_nodeinfo);
        struct ni_reply_data *data;
        data = (struct ni_reply_data *)&recvbuf[msglen];
        msglen += 4;
        msglen += 32;
  
        printf("\n");
        memcpy(ip1, data -> ip1.s6_addr, 16);
        memcpy(ip2, data -> ip2.s6_addr, 16);
  
        inet_ntop(AF_INET6, ip1, debug, 64);
        printf("%s\n", debug);
        inet_ntop(AF_INET6, ip2, debug, 64);
        printf("%s\n", debug);
  
  
  
  
  
        int namelen;
        char recvname[1500];
        memset(recvname, 0, 1500);
        namelen = transform_wired2string(data -> data, recvname, recvlen - msglen);
        printf("recvName: %s\n", recvname);

        char *tok_str;
        char temp_cut_str[10][256];
        tok_str = strtok(recvname, "\n");
        int p = 0;
        while(tok_str != NULL){
          strcpy(temp_cut_str[p], tok_str);
          tok_str = strtok(NULL, "\n");
          p++;
        }
        for(int i = 0; i < p; i++){
          printf("%d: %s\n", i, temp_cut_str[i]);
        }

        strcpy(dnsna, temp_cut_str[0]);
        strcpy(dnsna_sala, temp_cut_str[1]);

        printf("dnsna: %s\ndnsna_sala: %s\nIPv6: %s", dnsna, dnsna_sala, ip1);
        break;
      }
    }
  }


  ///////////////////
  // char temp_text[256];
  // memset(temp_text, 0, sizeof(temp_text));
  // struct stat buffer;
  // int sala_change = 0;
  // int exist = stat(dnsna, &buffer);
  // char mac[20]; memset(mac, 0, 20);

  // memset(temp_text, 0, sizeof(temp_text));
  // FILE* fptr = fopen("dnsna_list.txt","r+");
	// FILE* nfptr = fopen("dnsna_list.cmp.txt", "w");
  // char recv_mac[20]; memset(recv_mac, 0, 20);
  // // Get mac addr
  // int i = 0;
  ////////////////////
  
  //////////// save dnsna_list.txt ////////////
  
  FILE *fptr;
  FILE *nfptr;


  char temp_text[256];
  memset(temp_text, 0, sizeof(temp_text));
  struct stat buffer;
  int sala_change = 0;
  int exist = stat(dnsna, &buffer);
  char mac[20]; memset(mac, 0, 20);

  memset(temp_text, 0, sizeof(temp_text));
  fptr = fopen("dnsna_list.txt","r+");
	nfptr = fopen("dnsna_list.cmp.txt", "w");
  char recv_mac[20]; memset(recv_mac, 0, 20);
  // Get mac addr
  int i = 0;
  while(dnsna_sala[i] != '.') {
    recv_mac[i] = dnsna_sala[i];
    i++;
  }recv_mac[i] = '\0';
	
  isConflict = 0; 
	while (!feof(fptr)) {
		fscanf(fptr, "%s %s \n", mac, temp_text);
		printf("read\nmac : %s\ndns : %s\n", mac, temp_text);
		if (!isConflict&&strcmp(mac, recv_mac) == 0) {
			isConflict = 1;
			fprintf(nfptr, "%s %s\n", recv_mac, dnsna_sala);
			continue;
		}
		fprintf(nfptr, "%s %s\n", mac, temp_text);
	}

	if (!isConflict) {
		fprintf(fptr, "%s %s\n", recv_mac, dnsna_sala);
	}
	
	fclose(nfptr);
	fclose(fptr);
	if (!isConflict) {
		system("sudo rm dnsna_list.cmp.txt");
	}
	else {
        sala_change = 1;
		system("sudo mv -f dnsna_list.cmp.txt dnsna_list.txt");
	}
  ///////////////////////////////////////////

  if(sala_change){
    fptr = fopen("dnsna_update.file", "w");
    sprintf(text_buf, "server %s\n\nupdate delete %s AAAA\n\nsend\n",SERVER_IPV4, temp_text);
    printf("%s\n", text_buf);
    fprintf(fptr, "%s", text_buf);
    sprintf(text_buf, "/usr/bin/nsupdate -d -y rndc-key:%s %s",RNDC_KEY, "dnsna_update.file");
    printf("%s\n", text_buf);
    fclose(fptr);
    system(text_buf);
  }

  fptr = fopen("dnsna_update.file", "w");
  sprintf(text_buf, "server %s\n\nprereq nxdomain %s\n\nupdate add %s 300 IN AAAA %s\nsend\n", SERVER_IPV4, dnsna, dnsna, ipAddr);
  printf("%s\n", text_buf);
  fprintf(fptr, "%s", text_buf);
  sprintf(text_buf, "/usr/bin/nsupdate -d -y rndc-key:%s %s",RNDC_KEY, "dnsna_update.file");
  printf("%s\n", text_buf);
  fclose(fptr);
  system(text_buf);


  fptr = fopen("dnsna_update.file", "w");
  sprintf(text_buf, "server %s\n\nprereq nxdomain %s\n\nupdate add %s 300 IN AAAA %s\nsend\n", SERVER_IPV4, dnsna_sala, dnsna_sala, ipAddr);
  printf("%s\n", text_buf);
  fprintf(fptr, "%s", text_buf);
  sprintf(text_buf, "/usr/bin/nsupdate -d -y rndc-key:%s %s",RNDC_KEY, "dnsna_update.file");
  printf("%s\n", text_buf);
  fclose(fptr);
  system(text_buf);

  sprintf(text_buf, "sudo rndc thaw\n sudo systemctl restart bind9\nsudo cat /var/lib/bind/cpsdns.home.zone\n");
  system(text_buf);

  system("sudo rm dnsna_update.file");

}
