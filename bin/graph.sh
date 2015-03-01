rrdtool graph /var/www/sasacct/sas.gif --end -1d DEF:indatabytes=/var/sasacct/10.162.11.0.rrd:in:AVERAGE \
DEF:outdatabytes=/var/sasacct/10.162.11.0.rrd:out:AVERAGE \
AREA:indatabytes#00CC00:in LINE1:outdatabytes#0000FF:out
