#include "md5.h"
#include "ni_common.h"

static char UNIQUEID[SIZE_MACADDRESS_TEXT + 1];
static unsigned char MACADDRESS[SIZE_MACADDRESS_BINARY];
static unsigned char recvbuf[BUFSIZE];
static unsigned char sendbuf[BUFSIZE];
static unsigned char LOCAL_ADDRESS[SIZE_IPADDRESS_BINARY];
static unsigned char RA_PREFIX[SIZE_IPPREFIX_BINARY];
static unsigned char MD5_ADDRESS[SIZE_IPADDRESS_BINARY];
static unsigned char SOLICIT_MULTICAST_ADDRESS[SIZE_IPADDRESS_BINARY];
static char DNSSL[MAX_NAME_SIZE];
static char DNSNA[MAX_NAME_SIZE];
static char DNSNA_SALA[MAX_NAME_SIZE];
static char debug[SIZE_IPADDRESS_TEXT];

static void make_md5_iid(char *name, int namelen, uint8_t *iid);
int get_mac();
int proc_nd_ra(uint8_t *msg, int msglen);
int get_ipaddr();
int handle_nd_na(uint8_t *src, int msglen);

int main(){
  int sendlen;
  struct sockaddr_in6 from;
  int fromlen;
  int recvlen;
  //memset
  memset(recvbuf, 0x00, BUFSIZE);
  memset(sendbuf, 0x00, BUFSIZE);

  //set Socket
  int ni_socket;
  if((ni_socket = socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6)) < 0){
    perror("socket error");
    return -1;
  }
  setsockopt(ni_socket, SOL_SOCKET, SO_BINDTODEVICE, INTERFACE, strlen(INTERFACE));

  //get MAC
  get_mac();

  //Set ipv6 for ALL NODE
  struct sockaddr_in6 addr;
  memset(&addr, 0, sizeof(struct sockaddr_in6));
  addr.sin6_family = AF_INET6;
  inet_pton(AF_INET6, IPV6_LINKLOCAL_ALLNODE, &addr.sin6_addr);
  inet_ntop(AF_INET6, &addr.sin6_addr.s6_addr, debug, SIZE_IPADDRESS_TEXT);
  printf("ALLNODE: %s\n", debug);

  //Set ALL ROUTER
  struct sockaddr_in6 ar_addr;
  memset(&ar_addr, 0, sizeof(struct sockaddr_in6));
  ar_addr.sin6_family = AF_INET6;
  inet_pton(AF_INET6, IPV6_LINKLOCAL_ALLROUTER, &ar_addr.sin6_addr);
  inet_ntop(AF_INET6, &ar_addr.sin6_addr.s6_addr, debug, SIZE_IPADDRESS_TEXT);
  printf("ALLROUTER: %s\n", debug);

  //Create rs
  memset(sendbuf, 0x00, BUFSIZE);
  struct nd_router_solicit *nd_rs;
  nd_rs = (struct nd_router_solicit *)sendbuf;
  nd_rs -> nd_rs_type = ND_ROUTER_SOLICIT;
  nd_rs -> nd_rs_code = 0;
  nd_rs -> nd_rs_cksum = 0;
  nd_rs -> nd_rs_reserved = 0;
  sendlen = sizeof(struct nd_router_solicit);
  sendbuf[sendlen++] = ND_OPT_SOURCE_LINKADDR;
  sendbuf[sendlen++] = 0x01;
  memcpy(&sendbuf[sendlen], MACADDRESS, SIZE_MACADDRESS_BINARY);
  sendlen += SIZE_MACADDRESS_BINARY;

  //SEND RS
  if(sendto(ni_socket, sendbuf, sendlen, 0, (struct sockaddr *)&ar_addr, sizeof(ar_addr)) < 0){
    perror("sendto error");
    close(ni_socket);
    return -1;
  }

  //listenfor ra
  while(1){
    struct timeval tv;
    tv.tv_sec = 1;
    tv.tv_usec = 0;
    fd_set fds_s;
    FD_ZERO(&fds_s);
    FD_SET(ni_socket, &fds_s);
    if(select((ni_socket + 1), &fds_s, NULL, NULL, (struct timeval *)&tv) <= 0){
      continue;
    }
    if(FD_ISSET(ni_socket, &fds_s)){
      if((recvlen = recvfrom(ni_socket, recvbuf, sizeof(recvbuf), 0, (struct sockaddr *)&from, &fromlen)) < 0){
        printf("recvlen: %d\n", recvlen);
        perror("recvfrom error");
        return -1;
      }
      if(recvbuf[0] == ND_ROUTER_ADVERT){
        printf("routeradv_recvlen: %d\n", recvlen);
        printf("found router advertisement!\n");
        proc_nd_ra((uint8_t *)recvbuf, recvlen);
        break;
      }
    }
  }
  inet_ntop(AF_INET6, RA_PREFIX, debug, 64);
  printf("DNSSL: %s\nPrefix: %s\n",DNSSL, debug);


  get_ipaddr();
  inet_ntop(AF_INET6, LOCAL_ADDRESS, debug, 64);
  printf("LOCAL ADDRESS: %s\n", debug);
  for(int i = 0; i < SIZE_IPPREFIX_BINARY; i++){
    MD5_ADDRESS[i] = RA_PREFIX[i];
  }

  sprintf(UNIQUEID, "%02X%02X%02X%02X%02X%02X", (unsigned char)MACADDRESS[0]
                                              , (unsigned char)MACADDRESS[1]
                                              , (unsigned char)MACADDRESS[2]
                                              , (unsigned char)MACADDRESS[3]
                                              , (unsigned char)MACADDRESS[4]
                                              , (unsigned char)MACADDRESS[5]);

  printf("MAC ADDRESS: ");
  for(int i = 0; i < 6; i++){
    printf("%02X", (unsigned char)MACADDRESS[i]);
    if(i < 5){
      printf(":");
    }
  }
  printf("\n");

  //make dnsna
  int count = 1;
  if(1){
    sprintf(DNSNA, "%s.UID.%s.%s.x.y.COORD.%s.ROOM.%s.BUILDING.%s.LOC.%s",UNIQUEID, DEVICEMODEL, DEVICECATEGORY, ROOMNUM, BUILDING, LOCATION, DNSSL);
    printf("DNSNA: %s\n", DNSNA);
  }else{
    dnsna_change_flag:
    count++;
    sprintf(DNSNA, "%s.UID.%s.%s%d.x.y.COORD.%s.ROOM.%s.BUILDING.%s.LOC.%s",UNIQUEID, DEVICEMODEL, DEVICECATEGORY, count, ROOMNUM, BUILDING, LOCATION, DNSSL);
    printf("DNSNA: %s\n", DNSNA);
  }
  make_md5_iid(DNSNA, strlen(DNSNA), &MD5_ADDRESS[SIZE_IPPREFIX_BINARY]);
  inet_ntop(AF_INET6, MD5_ADDRESS, debug, 64);
  printf("MD5_ADDRESS: %s\n", debug);


  //Set Solicit Multicast Address
  struct sockaddr_in6 solicit_addr;
  memset(&solicit_addr, 0, sizeof(struct sockaddr_in6));
  solicit_addr.sin6_family = AF_INET6;
  printf("Setting UP Solicit Multicast Address ... \n");
  inet_pton(AF_INET6, "ff02::1:ffaa:aaa", SOLICIT_MULTICAST_ADDRESS);
  SOLICIT_MULTICAST_ADDRESS[13] = MD5_ADDRESS[13];
  SOLICIT_MULTICAST_ADDRESS[14] = MD5_ADDRESS[14];
  SOLICIT_MULTICAST_ADDRESS[15] = MD5_ADDRESS[15];
  memcpy(&solicit_addr.sin6_addr, SOLICIT_MULTICAST_ADDRESS, SIZE_IPADDRESS_BINARY);
  inet_ntop(AF_INET6, solicit_addr.sin6_addr.s6_addr, debug, SIZE_IPADDRESS_TEXT);
  printf("solicit_addr: %s\n\n", debug);


  //Create target
  struct in6_addr target;
  memcpy(&target.s6_addr, MD5_ADDRESS, SIZE_IPADDRESS_BINARY);


  //Create Neighbor Solicitation Message
  memset(sendbuf, 0x00, BUFSIZE);
  struct nd_neighbor_solicit *nd_ns;
  nd_ns = (struct nd_neighbor_solicit *)sendbuf;
  nd_ns->nd_ns_type = ND_NEIGHBOR_SOLICIT;
  nd_ns->nd_ns_code = 0;
  nd_ns->nd_ns_cksum  = 0;
  nd_ns->nd_ns_reserved = 0;
  nd_ns->nd_ns_target = target;
  sendlen = sizeof(struct nd_neighbor_solicit);
  sendbuf[sendlen++] = ND_OPT_SOURCE_LINKADDR;
  sendbuf[sendlen++] = 0x01;
  memcpy(&sendbuf[sendlen], MACADDRESS, 6);
  sendlen += 6;


  //Send Neighbor Solicitation Message
  time_t cur_time, old_time;
  int dad_message_counter = 2;
  while(1){
    if(sendto(ni_socket, sendbuf, sendlen, 0, (struct sockaddr *)&solicit_addr, sizeof(solicit_addr)) < 0){
      perror("sendto error: ");
      close(ni_socket);
      return -1;
    }
    printf("Sent DAD Message!\n");
    pretty_print_ns(sendbuf, sendlen, (uint8_t *)&solicit_addr.sin6_addr);
    old_time = time(NULL);
    while(1){
      cur_time = time(NULL);
      if(cur_time - old_time > DAD_INTERVAL){
        break;
      }
      //Listen For Neighbor Advertisement with identical ip
      struct timeval tv;
      tv.tv_sec = 1;
      tv.tv_usec = 0;
      fd_set select_fds;
      FD_ZERO(&select_fds);
      FD_SET(ni_socket, &select_fds);
      if(select((ni_socket + 1), &select_fds, NULL, NULL, (struct timeval *)&tv) <= 0){
        continue;
      }
      recvlen = recvfrom(ni_socket, recvbuf, sizeof(recvbuf), 0, (struct sockaddr *)&from, &fromlen);
      if(recvbuf[0] == ND_NEIGHBOR_ADVERT){
        printf("!!! Neighbor Advert !!!\n");
        pretty_print_na(recvbuf, recvlen, (uint8_t *)&from.sin6_addr);
        if(handle_nd_na(recvbuf, recvlen)){
          printf("       ============================\n");
          printf("       ============================\n");
          printf("       ============================\n");
          printf("       ==========Identical=========\n");
          printf("       ============================\n");
          printf("       ============================\n");
          printf("       ============================\n\n\n");
          printf("Changing IP Address...\n");
          goto dnsna_change_flag;
        }
      }
    }
    if(dad_message_counter == 1){
      memset(sendbuf, 0x00, BUFSIZE);
      printf("ENDING...\n");
      break;
    }
    dad_message_counter--;
  }
  printf("Finished DAD\n");


  FILE *fptr;
  fptr = fopen(SALA_UPDATE_FILE, "r");
  int x, y;
  fscanf(fptr, "%d %d", &x, &y);
  fclose(fptr);
  if(count == 1){
    sprintf(DNSNA_SALA, "%s.UID.%s.%s.%d.%d.COORD.%s.ROOM.%s.BUILDING.%s.LOC.%s",UNIQUEID, DEVICEMODEL, DEVICECATEGORY, x, y, ROOMNUM, BUILDING, LOCATION, DNSSL);
  }
  else{
    sprintf(DNSNA_SALA, "%s.UID.%s.%s%d.%d.%d.COORD.%s.ROOM.%s.BUILDING.%s.LOC.%s",UNIQUEID, DEVICEMODEL, DEVICECATEGORY, count, x, y, ROOMNUM, BUILDING, LOCATION, DNSSL);
  }
  printf("DNSNA_SALA: %s\n", DNSNA_SALA);
  char text_buf[256];

  struct stat buffer;
  char temp[64];
  int exist = stat("ipaddr.file", &buffer);
  if(exist == 0){
    fptr = fopen("ipaddr.file", "r");
    fgets(temp, sizeof(temp), fptr);
    sprintf(text_buf, "sudo ip -6 addr del %s/64 dev %s", temp, INTERFACE);
    printf("%s\n", text_buf);
    system(text_buf);
    memset(text_buf, 0, sizeof(text_buf));
    fclose(fptr);
  }


  inet_ntop(AF_INET6, MD5_ADDRESS, debug, SIZE_IPADDRESS_TEXT);
  sprintf(text_buf, "sudo ip -6 addr add %s/64 dev %s", debug, INTERFACE);
  printf("%s\n", text_buf);
  system(text_buf);
  fptr = fopen("ipaddr.file", "w");
  fprintf(fptr, "%s", debug);
  fclose(fptr);

  //Now DAD is Finished Send Neighbor Advertisement Regularly and when Neighbor Solicit is Received Send Neighbor Advertisement
  //Create Neighbor Advertisement
  struct nd_neighbor_advert *nd_na;
  memset(sendbuf, 0x00, BUFSIZE);
  nd_na = (struct nd_neighbor_advert *)sendbuf;
  nd_na -> nd_na_type = ND_NEIGHBOR_ADVERT;
  nd_na -> nd_na_code = 0;
  nd_na -> nd_na_cksum = 0;
  nd_na -> nd_na_flags_reserved = 0;
  nd_na -> nd_na_target = target;
  sendlen = sizeof(struct nd_neighbor_advert);
  sendbuf[sendlen++] = ND_OPT_TARGET_LINKADDR;
  sendbuf[sendlen++] = 0x01;
  memcpy(&sendbuf[sendlen], MACADDRESS, SIZE_MACADDRESS_BINARY);
  sendlen += 6;


  //listen for ni query and ns
  //Send Neighbor Advertisement + Listen for Neighbor Solicit
  memset(recvbuf, 0x00, BUFSIZE);
  while(1){
    if(sendto(ni_socket, sendbuf, sendlen, 0, (struct sockaddr *)&addr, sizeof(addr)) < 0){
      perror("sendto error");
      close(ni_socket);
      return -1;
    }
    printf("Sent Advertisement!\n");
    old_time = time(NULL);
    while(1){
      cur_time = time(NULL);
      if(cur_time - old_time > NA_INTERVAL){
        break;
      }

      struct timeval tv;
      tv.tv_sec = 1;
      tv.tv_usec = 0;
      fd_set select_fds;
      FD_ZERO(&select_fds);
      FD_SET(ni_socket, &select_fds);
      if(select((ni_socket + 1), &select_fds, NULL, NULL, (struct timeval *)&tv) <= 0){
        continue;
      }
      recvlen = recvfrom(ni_socket, recvbuf, sizeof(recvbuf), 0, (struct sockaddr *)&from, &fromlen);
      if(recvbuf[0] == ND_NEIGHBOR_SOLICIT){
        if(sendto(ni_socket, sendbuf, sendlen, 0, (struct sockaddr *)&addr, sizeof(addr)) < 0){
          perror("sendto error");
          close(ni_socket);
          return -1;
        }
      }
      else if(recvbuf[0] == ICMP6_NI_QUERY){
        //Read icmp query
        struct icmp6_nodeinfo *icmp6_query;
        icmp6_query = (struct icmp6_nodeinfo *)recvbuf;



        //Send icmp reply
        memset(sendbuf, 0x00, BUFSIZE);
        struct icmp6_nodeinfo *icmp6_reply;
        icmp6_reply = (struct icmp6_nodeinfo *)sendbuf;
        icmp6_reply -> ni_type = ICMP6_NI_REPLY;
        icmp6_reply -> ni_code = NI_REPLY_CODE_SUCC;
        icmp6_reply -> ni_cksum = 0;
        icmp6_reply -> ni_qtype = icmp6_query -> ni_qtype;
        icmp6_reply -> ni_flags = 0;
        memcpy(icmp6_reply -> ni_nonce, icmp6_query -> ni_nonce, 8);
        sendlen = sizeof(struct icmp6_nodeinfo);

        struct ni_reply_data *replymsg;
        replymsg = (struct ni_reply_data *)&sendbuf[sendlen];
        replymsg -> ttl = 0;
        for(int i = 0; i < 16; i++){
          replymsg -> ip1.s6_addr[i] = LOCAL_ADDRESS[i];
        }
        for(int i = 0; i < 16; i++){
          replymsg -> ip2.s6_addr[i] = MD5_ADDRESS[i];
        }

        char msg_buf[BUFSIZE];
        sprintf(msg_buf,"\n%s\n%s\n", DNSNA, DNSNA_SALA);
        printf("%s\n", msg_buf);
        int tmp_len;
        tmp_len = transform_string2wired(msg_buf, replymsg->data, strlen(msg_buf));

        sendlen += (4 + 32 + tmp_len);

        printf("%d\n", sendlen);
        if(sendto(ni_socket, sendbuf, sendlen, 0, (struct sockaddr *)&from, sizeof(from)) < 0){
          perror("sendto error");
          return -1;
        }
      }
    }

    //update sala
    fptr = fopen(SALA_UPDATE_FILE, "r");
    int x, y;
    fscanf(fptr, "%d %d", &x, &y);
    fclose(fptr);
    if(count == 1){
      sprintf(DNSNA_SALA, "%s.UID.%s.%s.%d.%d.COORD.%s.ROOM.%s.BUILDING.%s.LOC.%s",UNIQUEID, DEVICEMODEL, DEVICECATEGORY, x, y, ROOMNUM, BUILDING, LOCATION, DNSSL);
    }
    else{
      sprintf(DNSNA_SALA, "%s.UID.%s.%s%d.%d.%d.COORD.%s.ROOM.%s.BUILDING.%s.LOC.%s",UNIQUEID, DEVICEMODEL, DEVICECATEGORY, count, x, y, ROOMNUM, BUILDING, LOCATION, DNSSL);
    }
    printf("DNSNA_SALA: %s\n", DNSNA_SALA);

  }
}

int proc_nd_ra(uint8_t *msg, int msglen){
  struct nd_router_advert *nd_ra;
  struct nd_opt_hdr *opt;
  int optlen;
  struct nd_opt_dnssl *opt_dnssl = NULL;
  struct nd_opt_prefix *opt_prefix  = NULL;
  int hdlen, dnssl_pos, prefix_pos;

  nd_ra = (struct nd_router_advert *)msg;
  hdlen = sizeof(struct nd_router_advert);
  while(hdlen < msglen){
    opt = (struct nd_opt_hdr *)&msg[hdlen];
    if(opt -> nd_opt_type == ND_OPT_DNSSL){
      opt_dnssl = (struct nd_opt_dnssl *)opt;
      dnssl_pos = hdlen;
    }
    else if(opt->nd_opt_type == ND_OPT_PREFIX){
      opt_prefix = (struct nd_opt_prefix *)opt;
      prefix_pos = hdlen;
    }
    hdlen += (opt->nd_opt_len << 3);
  }
  optlen = (opt_dnssl->nd_opt_dnssl_len << 3);

  dnssl_pos += sizeof(struct nd_opt_dnssl);
  prefix_pos += sizeof(struct nd_opt_prefix);
  int sublen;
  int temp = 0;
  optlen -= sizeof(struct nd_opt_dnssl);
  transform_wired2string(&msg[dnssl_pos], DNSSL, optlen);

  for(int i = 0; i < ((opt_prefix -> nd_opt_prefix_len << 3) - sizeof(struct nd_opt_prefix)); i++){
    RA_PREFIX[i] = msg[prefix_pos + i];
  }
}
int get_mac(){
	struct ifconf ifc;
	struct ifreq *ifr , *r;
	int sok_mac;
	memset(&ifc, 0, sizeof(ifc));
	ifc.ifc_ifcu.ifcu_req = NULL;
	ifc.ifc_len = 0;
	sok_mac = socket(PF_INET, SOCK_DGRAM, 0);
	ioctl(sok_mac, SIOCGIFCONF, &ifc);
	ifr = (struct ifreq *)malloc(ifc.ifc_len);
	ifc.ifc_ifcu.ifcu_req = ifr;
	ioctl(sok_mac, SIOCGIFCONF,&ifc);
	int num;
	num = ifc.ifc_len/sizeof(struct ifreq);
	for(int i=0; i<num; i++){
		r=&ifr[i];
		if(!strcmp(r->ifr_name, INTERFACE)){
			ioctl(sok_mac, SIOCGIFHWADDR, r);
			memcpy(MACADDRESS, (uint8_t*)r->ifr_hwaddr.sa_data, SIZE_MACADDRESS_BINARY);
			break;
		}
	}
}
static void make_md5_iid(char *name, int namelen, uint8_t *iid){
  md5_state_t state;
  md5_byte_t digest[16];
  md5_init(&state);
  md5_append(&state, (const md5_byte_t *)name, namelen);
  md5_finish(&state, digest);
  memcpy(iid, digest, SIZE_IPPREFIX_BINARY);
}
int get_ipaddr(){
  int check = 1;
  struct ifaddrs *ifa_t;
  getifaddrs(&ifa_t);
  int family;
  for(ifa_t; ifa_t != NULL; ifa_t = ifa_t -> ifa_next){
    family = ifa_t -> ifa_addr -> sa_family;
    if(family == AF_INET6 && !strcmp(ifa_t -> ifa_name, INTERFACE)){
      for(int i = 0; i < 8; i++){
        if(RA_PREFIX[i] != ifa_t->ifa_addr->sa_data[6+i]){
          check = 0;
          break;
        }
      }
      if(check){
        for(int i = 0; i < 16; i++){
          LOCAL_ADDRESS[i] = ifa_t -> ifa_addr -> sa_data[6 + i];
        }
      }
    }
  }
}
int handle_nd_na(uint8_t *src, int msglen){
  int check = 1;
  unsigned char target_ip[SIZE_IPADDRESS_BINARY];
  unsigned char source_mac[SIZE_MACADDRESS_BINARY];
  struct nd_neighbor_advert *nd_na_in;

  nd_na_in = (struct nd_neighbor_advert *)src;
  for(int i = 0; i < 16; i++){
    target_ip[i] = nd_na_in->nd_na_target.s6_addr[i];
  }
  for(int i = 0; i < SIZE_IPADDRESS_BINARY; i++){
    if(target_ip[i] != MD5_ADDRESS[i]){
      check = 0;
      break;
    }
  }
  return check;
}
