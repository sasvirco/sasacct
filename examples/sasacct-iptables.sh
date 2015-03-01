#!/bin/sh
# modified from sasacct-ipchains
# file containing the ips one per line
IPFILE='sasacct-ips'
iptables -N SASACCT
iptables -I INPUT -j SASACCT
iptables -I OUTPUT -j SASACCT
iptables -I FORWARD -j SASACCT
grep "^" $IPFILE | while read ip;
do
        /sbin/iptables -I SASACCT  -s 0.0.0.0/0 -d $ip
        /sbin/iptables -I SASACCT -s $ip     -d 0.0.0.0/0 
done
