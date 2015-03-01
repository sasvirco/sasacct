#!/usr/bin/perl -w
use strict;
my %snmp;
my $conf = $ARGV[0];
use RRDs;
use Carp;
my $logdir;
my $graphdir;
use File::Copy;
if (!defined($ARGV[0])) {
	print ("supply configfile with -c\n");
	exit;
}
open(CONF,"<$conf") || croak ("Cannot open file $conf: $!");
#Parse config and generate hash , keys are rrd files,values are pointers to array
while (<CONF>) {
        if ($_ =~ /^snmp/) {
        chop $_;
        s/^snmp://g;
        my ($file,@i)=split(/:/,$_);
        $snmp{$file}=\@i if !defined($snmp{$file});
        }
        if ($_ =~ /^logdir/){
        chop $_;
        s/^logdir://g;
        # Remove the "/" sufix if exists and add it again
        # fazzter than checking for it
        s/\/$//g;     # the black magic
        $_ = $_."\/"; # goes here,seems unusable but fixes pain in the ass
        $logdir = $_;
        }
        if ($_ =~ /^graphdir/){
        chop $_;
        s/^graphdir://g;
        s/\/$//g;
        $_ = $_."\/";
        $graphdir = $_;
        }
}
close CONF;
open (NEWCNF,">$logdir"."sastragraph.conf.new") || croak ("Cannot open file: $!");
my $count = 0;
for(keys(%snmp)) {
	RRDs::tune( $_,
	"-d","in:ABSOLUTE",
	"-d","out:ABSOLUTE"
	 );
	if (stat("$logdir"."$_")){
	move("$logdir"."$_","$logdir"."$snmp{$_}->[1]"."_"."$snmp{$_}->[0]".'.rrd');
	}
	#file syntax->snmp:filename:interfacenumber:router:communityname:type:graphtitle
	#snmp:clientname:routerip:interface:community:graphtitle 
	print ("$logdir$_ moved to $logdir$snmp{$_}->[1]_$snmp{$_}->[0].rrd\n");
	print NEWCNF ("snmp:client$count:$snmp{$_}->[1]:$snmp{$_}->[0]:$snmp{$_}->[2]:$snmp{$_}->[4]\n");
	$count = $count + 1 ;
}
print NEWCNF ("logdir:$logdir\ngraphdir:$graphdir\n");
close NEWCNF;
print ("You should now check and edit your sastragraph.conf.new\n");
print ("and replace it with your old sastragraph.conf.\n");
print ("Edit the second field clients[0-9] and type there\n");
print ("some name (unique) for every interface/router pair\n");
