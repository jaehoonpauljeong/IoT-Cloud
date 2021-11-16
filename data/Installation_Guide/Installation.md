# Installation Guide

### Setting RADVD

```bash
$ sudo apt-get install radvd 
```

After installing radvd, go to etc/radvd.conf file and edit it like this.
```
interface wlan0
{
  AdvSendAdvert on;
  MinRtrAdvInterval 600;
  MaxRtrAdvInterval 1800;
  prefix 2001:1ba:23:122::/64
  {
    AdvOnLink on;
    AdvAutonomous on;
    AdvRouterAddr on;
  };
  RDNSS 2001:1ba::1
  {
    AdvRDNSSLifetime 3600;
  };
  DNSSL .cpslab.skku.edu
  {
    AdvDNSSLLifetime 3600;
  };
}; 
``` 
<br/>

After this, you can run radvd by entering: <br/>
```bash
$ sudo systemctl start radvd 
```
Check status by entering following command.
```bash
$ sudo systemctl status radvd 
```
___

### Setting Bind9

```bash
$ sudo apt-get install bind9
```
After installing bind9, go to _/etc/bind/_ and edit named.conf file.
```
include "/etc/bind/named.conf.default-zones";

options {
  listen-on-v6{ any; };
  directory "/var/lib/bind";
  allow-recursion {
    127.0.0.1;
    172.30.1.18;
  };
  allow-transfer { ANY; };
  allow-query { ANY; };
};
key "rndc-key" {
  algorithm hmac-md5;
  secret "##############";
};

controls{
  inet 127.0.0.1 port 953
  allow { 127.0.0.1; } keys {"rndc-key";};
};

zone "cpslab.skku.edu" IN {
  type master;
  file "/var/lib/bind/cpsdns.home.zone";
  allow-update{ key "rndc-key"; };
  notify no;
};
```
<br/>

**In the secret at rndc key part, check your rndc key** at _/etc/bind/rndc.key_.

We have setted zone file in _var/bind/cpsdns.home.zone_. So we config cpsdns.home.zone file.
```
$ORIGIN .
$TTL 300  ; 5 minutes
cpslab.skku.edu         IN SOA ns.cpslab.skku.edu. root.cpslab.skku.edu. (
                               202012337 ; serial
                               21600 ; refresh (6 hours)
                               1800 ; retry (30 minutes)
                               2419200 ; expire (4 weeks)
                               86400 ; minimum (1 day)
                               )
                            NS ns.cpslab.skku.edu.
                            A  172.30.1.18
$ORIGIN cpslab.skku.edu.
ns                          A 172.30.1.18
                            AAAA 2001:1ba:23:122:d600:4985:e78c:d930                         
```

After finishing config file, type following command and check whether it has problem.
```bash
$ sudo systemctl status bind9
```


### Android Specification
We are using Android 5.0 (Lollipop) API 21 and it is working well at Android 10.0(API 29), Android 11.0(API 30).

### Java Specification
We are using Java 11 SDK 11.0.9. We have developed  under "Intellij IDEA 2020" so, we recommend to operate on Intellij IDEA 2020.
If you face UTF-8 problem, follow under guide.<br>
<ol>
 <li>(If intellij IDEA) Go to Help-> Edit Custom VM Options...<br>
 <li>Add <strong>-Dfile.encoding=UTF-8</strong> at the last line.<br>
</ol>


