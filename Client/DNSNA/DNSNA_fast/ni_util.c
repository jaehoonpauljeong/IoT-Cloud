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
