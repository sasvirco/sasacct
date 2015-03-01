# sasacct
SASacct is accounting package, used for collecting traffic statistics using internal OS specific kernel counters or using SNMP. 

This is 1.0.3 release of SAS's accounting statistics. It contains 3 programs for collecting statistics for used traffic and create graphics with bandwith tilization:

* sasacct.plx     (for doing ip accouting using iptables,ipchains,pf,ipf)
* sastragraph.plx (for doing per interface accounting via snmp)
* cimon.plx       (for doing ip accounting using cisco routers and cisco ip accounting feature)

For further details how to setup them please read:
               
* docs/sasacct - for how to configure sasacct
* docs/cimon - for cisco ip accounting(via snmp) 
* docs/sastragraph - for accounting via snmp

See the CHANGES file in every documentation
directory.

* etc/ directory contains the configuration files for the accounting packages.
* bin/ directory contains the executable files. The one you don't already know nothing about is htmlmaker.plx.  It creates html files with bandwith utilization 
graphics for accounted hosts.
* cgi-bin/ contains  cgi script that must be placed in the cgi-bin directory
of your httpd server.
* sasacct.cgi   - you use this to see traffic statistics from date to date with username/password authentication. Uses CGI::Sessions for  session management. 
                
For further details how to setup the cgi scripts
please read cgi-bin/README.
                                                                             
Enjoy!!!

P.S Sometimes I cannot sleep thinkingt hat there is better way to do
the job, so free my sleep , feel free to send sms 359888575795@sms.mtel.net)with this simple words (Hello World). It will make me vary happy. And please do not use MS Outlook for this.
