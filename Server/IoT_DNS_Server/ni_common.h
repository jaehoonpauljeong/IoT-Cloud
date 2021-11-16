/*Node Information
  Following Header file holds information used for both ni_gateway and ni_node
*/

#include <ifaddrs.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <net/if_arp.h>
#include <netinet/in.h>
#include <netinet/ether.h>
#include <netinet/ip6.h>
#include <netinet/icmp6.h>
#include <errno.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include <sys/stat.h>

#define IPV6_LINKLOCAL_ALLNODE        "ff02::1"
#define IPV6_LINKLOCAL_ALLROUTER      "ff02::2"

#define BUFSIZE               1500
#define SIZE_IPADDRESS_BINARY 16
#define SIZE_IPADDRESS_TEXT   64
#define SIZE_IPPREFIX_BINARY  8
#define INTERFACE             "wlan0"
#define ND_OPT_DNSSL          31
#define ND_OPT_PREFIX         3
#define DEVICEMODEL           "raspPi"
#define DEVICECATEGORY        "LED"
#define ROOMNUM               "400609"
#define BUILDING              "semicond"
#define LOCATION              "skku"
#define SIZE_MACADDRESS_BINARY  6
#define SIZE_MACADDRESS_TEXT    12
#define MAX_NAME_SIZE           256
#define ICMP6_NI_QUERY          139
#define ICMP6_NI_REPLY          140
#define NI_REPLY_CODE_SUCC      0
#define NI_QUERY_CODE_IPV6      0
#define NI_QTYPE_NODENAME       2
#define DAD_INTERVAL 10 //in seconds
#define NA_INTERVAL 30//in seconds
#define GATE_INTERVAL 60// in seconds
#define RNDC_KEY                "y6fF7WDWR2AlB5I3lTmBOQ=="
#define SERVER_IPV4             "192.168.1.74"
#define SALA_UPDATE_FILE        "coordinate.file"

struct nd_opt_dnssl{
  uint8_t nd_opt_dnssl_type;
  uint8_t nd_opt_dnssl_len;
  uint16_t nd_opt_dnssl_reserved;
  uint32_t nd_opt_dnssl_lifetime;
  //After so dnssl
};

struct nd_opt_prefix{
  uint8_t nd_opt_prefix_type;
  uint8_t nd_opt_prefix_len;
  uint8_t nd_opt_prefix_flag;
  uint32_t nd_opt_prefix_v_liftime;
  uint32_t nd_opt_prefix_p_lifetime;
  uint32_t nd_opt_prerfix_reserved;
  //After so prefix
};

struct icmp6_nodeinfo{
  struct icmp6_hdr icmp6_ni_hdr;
  uint8_t          icmp6_ni_nonce[8];
};

#define ni_type       icmp6_ni_hdr.icmp6_type
#define ni_code       icmp6_ni_hdr.icmp6_code
#define ni_cksum      icmp6_ni_hdr.icmp6_cksum
#define ni_qtype      icmp6_ni_hdr.icmp6_data16[0]
#define ni_flags      icmp6_ni_hdr.icmp6_data16[1]
#define ni_nonce      icmp6_ni_nonce

struct ni_reply_data{
  uint32_t  ttl;
  struct in6_addr  ip1;
  struct in6_addr  ip2;
  uint8_t   data[1];
};

int transform_string2wired(char *in, uint8_t *out, int len);
int transform_wired2string(uint8_t *in, char *out, int len);
void pretty_print_na(uint8_t *src, int msglen, uint8_t *ipaddr);
void pretty_print_ns(uint8_t *src, int msglen, uint8_t *ipaddr);
