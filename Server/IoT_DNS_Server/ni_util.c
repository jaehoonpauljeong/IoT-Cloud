
#include "ni_common.h"

int transform_wired2string(uint8_t *in, char *out, int len){

  int i = 0;
  int j = 0;
  int sublen = 0;

  while(i < len){

    sublen = in[i++];
    if(sublen == 0){
      if(in[i] == 0)
        break;

      continue;
    }

    if(j) out[j++] = '.';
    memcpy(&out[j], &in[i], sublen);
    i += sublen;
    j += sublen;
  }
  out[j] = '\0';

  return j;
}

int transform_string2wired(char *in, uint8_t *out, int len){
  int i = 0;
  int j = 0;
  int sublen = 0;
  int pos = 0;

  while(i < len){
    if(in[i] == '\0'){
      break;
    }

    if(in[i++] != '.'){
      sublen++;
      continue;
    }

    out[j++] = sublen;
    memcpy(&out[j], &in[pos], sublen);
    j += sublen;
    pos = i;
    sublen = 0;
  }

  if(sublen){
    out[j++] = sublen;
    memcpy(&out[j], &in[pos], sublen);
    j += sublen;
  }
  out[j++] = 0;
  out[j++] = 0;
  return j;
}

void pretty_print_na(uint8_t *src, int msglen, uint8_t *ipaddr){
  unsigned char target_ip[SIZE_IPADDRESS_BINARY];
  char debug[SIZE_IPADDRESS_TEXT];
  unsigned char source_mac[SIZE_MACADDRESS_BINARY];
  int hdlen;
  struct nd_neighbor_advert *nd_na_in;

  nd_na_in = (struct nd_neighbor_advert *)src;
  hdlen = sizeof(struct nd_neighbor_advert);
  hdlen += 2; //Advertisement holds can hold other options. just for convinience for now leave it like this but should change
  for(int i = 0; i < 16; i++){
    target_ip[i] = nd_na_in->nd_na_target.__in6_u.__u6_addr8[i];
  }
  for(int i = 0; i < 6; i++){
    source_mac[i] = src[hdlen + i];
  }
  printf("\n\n");
  printf("  +==========NEIGHBOR_ADVERTISEMENT===========+\n");
  inet_ntop(AF_INET6, ipaddr, debug, SIZE_IPADDRESS_TEXT);
  printf("  | from:%s            |\n", debug);
  printf("  +                                           +\n");
  inet_ntop(AF_INET6, target_ip, debug, SIZE_IPADDRESS_TEXT);
  printf("  | target:%s|\n",debug);
  printf("  + belongs to                                +\n");
  printf("  | %02X:%02X:%02X:%02X:%02X:%02X                         |\n"
                                            , (unsigned char)source_mac[0]
                                            , (unsigned char)source_mac[1]
                                            , (unsigned char)source_mac[2]
                                            , (unsigned char)source_mac[3]
                                            , (unsigned char)source_mac[4]
                                            , (unsigned char)source_mac[5]);
  printf("  +                                           +\n");
  printf("  +===========================================+\n");
  printf("\n\n");
}
void pretty_print_ns(uint8_t *src, int msglen, uint8_t *ipaddr){
  unsigned char target_ip[SIZE_IPADDRESS_BINARY];
  char debug[SIZE_IPADDRESS_TEXT];
  unsigned char source_mac[SIZE_MACADDRESS_BINARY];
  int hdlen;
  struct nd_neighbor_advert *nd_na_in;

  nd_na_in = (struct nd_neighbor_advert *)src;
  hdlen = sizeof(struct nd_neighbor_advert);
  hdlen += 2; //Advertisement holds can hold other options. just for convinience for now leave it like this but should change
  for(int i = 0; i < 16; i++){
    target_ip[i] = nd_na_in->nd_na_target.__in6_u.__u6_addr8[i];
  }
  for(int i = 0; i < 6; i++){
    source_mac[i] = src[hdlen + i];
  }
  printf("\n\n");
  printf("  +=========NEIGHBOR_SOLICIT_MESSAGE==========+\n");
  inet_ntop(AF_INET6, ipaddr, debug, SIZE_IPADDRESS_TEXT);
  printf("  | TO:%s                      |\n", debug);
  printf("  +                                           +\n");
  inet_ntop(AF_INET6, target_ip, debug, SIZE_IPADDRESS_TEXT);
  printf("  | target:%s\n",debug);
  printf("  + Query from                                +\n");
  printf("  | %02X:%02X:%02X:%02X:%02X:%02X                         |\n"
                                            , (unsigned char)source_mac[0]
                                            , (unsigned char)source_mac[1]
                                            , (unsigned char)source_mac[2]
                                            , (unsigned char)source_mac[3]
                                            , (unsigned char)source_mac[4]
                                            , (unsigned char)source_mac[5]);
  printf("  +                                           +\n");
  printf("  +===========================================+\n");
  printf("\n\n");
}
