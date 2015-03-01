#!/bin/sh
# Author: Spas Guevski, email: spas@bitex.com
# Modified: Alexandar Zheliazkov: sasvirco@homemail.com
# Modify this file to fit your needs
# replace iface with your interface (if needed)
# replace also IPFILE to point to your file
IPFILE='sasacct-ips' #file containint the ips one per line
/sbin/ipchains -F
/sbin/ipchains -X
/sbin/ipchains -N SASACCTI
/sbin/ipchains -N SASACCTO
/sbin/ipchains -I input -j SASACCTI
/sbin/ipchains -I output -j SASACCTO

grep "^" $IPFILE | while read ip;
do
        /sbin/ipchains -I SASACCTI  -s 0.0.0.0/0 -d $ip     -i iface 
        /sbin/ipchains -I SASACCTO -s $ip     -d 0.0.0.0/0 -i iface
done
