#include "ni_common.h"

static unsigned char IPADDRESS[SIZE_IPADDRESS_BINARY];
static unsigned char recvbuf[BUFSIZE];
static unsigned char sendbuf[BUFSIZE];
static unsigned char DNSSL[MAX_NAME_SIZE];
static unsigned char DNSNA[MAX_NAME_SIZE];
static char debug[SIZE_IPADDRESS_TEXT];
static unsigned char MACADDRESS[SIZE_MACADDRESS_BINARY];
int get_mac();
int proc_nd_ra(uint8_t *msg, int msglen);

int main(){
  get_mac();

  int sendlen;
  struct sockaddr_in6 from;
  int fromlen;
  int recvlen;


  //memset
  memset(recvbuf, 0x00, BUFSIZE);
  memset(sendbuf, 0x00, BUFSIZE);

  //Create socket
  int ni_socket;
  if((ni_socket = socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6)) < 0){
    perror("Socket Error");
    return -1;
  }
  setsockopt(ni_socket, SOL_SOCKET, SO_BINDTODEVICE, INTERFACE, strlen(INTERFACE));

  /*Router Solicitation Message Section*/
  //Set All ROUTER
  struct sockaddr_in6 ar_addr;
  memset(&ar_addr, 0, sizeof(struct sockaddr_in6));
  ar_addr.sin6_family = AF_INET6;
  inet_pton(AF_INET6, IPV6_LINKLOCAL_ALLROUTER, &ar_addr.sin6_addr);
  inet_ntop(AF_INET6, &ar_addr.sin6_addr.s6_addr, debug, SIZE_IPADDRESS_TEXT);
  printf("ALL Node: %s\n", debug);

  //Create RS Message
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



  /*Listen For Router Advertisement*/
  //listen for RA (GET DNSSL)
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
        perror("recvfrom error");
        return -1;
      }
      if(recvbuf[0] == ND_ROUTER_ADVERT){
        proc_nd_ra((uint8_t *)recvbuf, recvlen);
        break;
      }
    }
  }
  printf("DNSSL: %s\n", DNSSL);

  int x, y;
  /*Make DNSNA*/
  FILE *fptr;
  fptr = fopen("coordinate.file", "r");
  fscanf(fptr, "%d %d", &x, &y);
  fclose(fptr);
  sprintf(DNSNA, "LED.%d.%d.TEST.%s", x, y, DNSSL);
  printf("DNSNA: %s\n", DNSNA);

  printf("Ready...\n Can Receive ICMP NODE QUERY NOW\n");

  time_t cur_time, old_time;

  /*Listen for ICMP NODE QUERY*/
  while(1){
    FILE *fptr;
    fptr = fopen("coordinate.file", "r");
    fscanf(fptr, "%d %d", &x, &y);
    fclose(fptr);
    sprintf(DNSNA, "LED.%d.%d.TEST.%s", x, y, DNSSL);
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
      if(FD_ISSET(ni_socket, &select_fds)){
        recvlen = recvfrom(ni_socket, recvbuf, sizeof(recvbuf), 0, (struct sockaddr *)&from, &fromlen);
        if(recvbuf[0] == ICMP6_NI_QUERY){
          //Received ICMP Node QUERY
          struct icmp6_nodeinfo *icmp6_query;
          icmp6_query = (struct icmp6_nodeinfo *)recvbuf;

          //Create icmp reply
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

          //Create reply data
          struct ni_reply_data *replymsg;
          replymsg = (struct ni_reply_data *)&sendbuf[sendlen];
          replymsg -> ttl = 0;
          char msg_buf[BUFSIZE];
          sprintf(msg_buf, "\n%s\n", DNSNA);
          int tmp_len;
          tmp_len = transform_string2wired(msg_buf, replymsg -> data, strlen(msg_buf));
          sendlen += (4 + tmp_len);
          if(sendto(ni_socket, sendbuf, sendlen, 0, (struct sockaddr *)&from, sizeof(from)) < 0){
            perror("Sendto error");
            return -1;
          }
        }
      }
    }
  }

}


int proc_nd_ra(uint8_t *msg, int msglen){
  struct nd_router_advert *nd_ra;
  struct nd_opt_hdr *opt;
  int optlen;
  struct nd_opt_dnssl *opt_dnssl = NULL;
  int hdlen, dnssl_pos;

  nd_ra = (struct nd_router_advert *)msg;
  hdlen = sizeof(struct nd_router_advert);
  while(hdlen < msglen){
    opt = (struct nd_opt_hdr *)&msg[hdlen];
    if(opt -> nd_opt_type == ND_OPT_DNSSL){
      opt_dnssl = (struct nd_opt_dnssl *)opt;
      dnssl_pos = hdlen;
    }
    hdlen += (opt -> nd_opt_len << 3);
  }
  optlen = (opt_dnssl -> nd_opt_dnssl_len << 3);

  dnssl_pos += sizeof(struct nd_opt_dnssl);
  int sublen;
  optlen -= sizeof(struct nd_opt_dnssl);
  transform_wired2string(&msg[dnssl_pos], DNSSL, optlen);

  return 1;
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
