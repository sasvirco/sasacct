#!/usr/bin/perl 
use strict;
use CGI::Carp('fatalsToBrowser');
use CGI::Pretty qw(:all);
use Time::Local;
my $q = new CGI;
my $startdate=(param('syear').param('smonth').param('sday'));
my $enddate=(param('eyear').param('emonth').param('eday'));
my $dograph = $q->param('graph');
my $bits = $q->param('bits');
my $zoom = $q->param('zoom');
my $ip=$q->param('ip');
my %remote;
my %rkeys;
my %local;
my ($sec,$min,$hour,$mday,$mon,$year) = localtime();
my $system_time = sprintf("%04d%02d%02d% 02d%02d%02d", ($year+1900), $mon+1, $mday, $hour, $min, $sec);
my @years = (2001,2002,2003);
my %mlabels= ('01' => 'Jan','02' => 'Feb','03' => 'Mar','04' => 'Apr','05' => 'May','06' =>'Jun','07' => 'Jul',
		 '08' =>  'Aug','09' => 'Sep',10 => 'Oct',11=>'Nov',12 => 'Dec');
my @months =('01','02','03','04','05','06','07','08','09','10','11','12');
my @days = qw(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31);
my $sdateformated = (param('sday').'-'.param('smonth').'-'.param('syear'));
my $edateformated = (param('eday').'-'.param('emonth').'-'.param('eyear'));

#EDIT HERE 
my $configfile = "/etc/sasacct.conf";
my $logopath = '/sasacct';
#STOP EDITING

#Parse configfile

open(CNF,"$configfile");
while(<CNF>) {
        if ($_ =~ /^D/ && !exists($rkeys{D})) {
        chop $_;
        s/^D://g;
	    s/\/$//g;
        $_ = $_."\/";
	    $rkeys{D} = $_;
        }
        if ($_ =~ /^L/){
        chop $_;
        s/^L://g;
        my ($ip,@i)=split(/:/,$_);
        $local{$ip}= \@i if !defined($local{$ip});
        }
        if ($_ =~ /^R/) {
        chop $_;
        s/^R://g;
        my ($ip,@j)=split(/:/,$_);
        $remote{$ip}=\@j if !defined($remote{$ip});
        }
}
close CNF;

#Generate array containing the ips
my @ips;
if (stat($rkeys{D})) {
	opendir DIR,$rkeys{D} || die ("Cannot open: $!");
	my @files = readdir(DIR);
	closedir DIR;
	for(@files) {
	if ($_ =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\_\d+)*?$/ && $_ !~ /rrd/g){ 
	push @ips,$_;
		}
	}
}
@ips = sort @ips;

push @ips,"All";

#begin html data
if ($q->param('textmode') == 1) {
	my ($in,$out) = &gen_traff($startdate,$enddate,$ip);
	if ($in && $out) {
		print header('text/plain');
		print ("$ip $in $out\n");
		exit;
	}

}
print header();
print start_html(
-title => 'SASacct Accounting Statistics',
-head=>meta({-http_equiv => 'Page-enter',-content=>'filter: blendtrans(duration=0.5)'}),
-style => (
'.title {font-family:Verdana,Helvetica,Arial,sans-serif; font-size: 12px; font-weight: normal; color: #666666}
.default {font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000}
.small {font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 9.5px; color: #666666}
#.input {background: #FFFFFF; font-family:Verdana,Arial,Helvetica;font-size: 8pt; border: 1px solid #666666; padding: 1px;color: #666666}
.select {background: #ffffff; FONT-FAMILY: verdana; FONT-SIZE: 12pt; border: 1px solid black; padding: 2px;color: #000000}
.negative {color: #FFFFFF; background-color: #666666; font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 12px}'
),
-bgcolor => '#FFFFFF', -text =>'#666666', -vlink =>'#666666', -alink =>'#009900' -link =>'#333333'
);
print center,img({src=>"$logopath/salogo.gif"}),
		p({-class=>"title"},'<b>[Traffic Statistics]</b>');
print hr;
if (defined($startdate) && defined($enddate)) {
	my ($in,$out) = &gen_traff($startdate,$enddate,$ip);
	print &gen_form();
	#print hr;
	if (defined($in) && defined($out)){
	print center,
	p({class=>"default"},"Total traffic from <b>$sdateformated</b> to <b>$edateformated</b> for $ip ($local{$ip}[0])");
	my $total = $in+$out;
	my $totalmb = sprintf("%.3f", $total/1024/1024); 
	print table({-celpadding => '0' ,-class=>'default', -cellspacing =>'0' , -border => '0'},
	Tr({-bgcolor=> '#C0C0C0'},
	th(['Ip Number','Input Traffic[bytes]','Output Traffic[bytes]',
		'Total [bytes]','Total [MBytes]'])),
	Tr({-valign =>"middle",-align =>"middle"},
	td(["$ip","$in","$out","$total","$totalmb"])));
	}
	# Decide what will we graph
	if ($dograph eq 'on' && $ip ne "All" ){
	my $utcstart  = timelocal('00','00','00',param('sday'),param('smonth')-1,param('syear'));
        my $utcend = timelocal('00','00','00',param('eday'),param('emonth')-1,param('eyear'));
	($utcend = $utcstart + 86000) if ($utcstart == $utcend);
	($bits eq "on") ? ($bits = 1) : ($bits = 0);
	($zoom eq "on") ? ($zoom = 1): ($zoom = 0);
	my $fpathrrd = $rkeys{D}.param('ip').".rrd";
	print br,br;
	#On the fly graph goes here.
	if ( -f ("$fpathrrd") && ($utcstart < $utcend)) {
	print img({-src => "/cgi-bin/showgraph.cgi?utcstart=$utcstart&utcend=$utcend&file=$fpathrrd&bits=$bits&zoom=$zoom"});
		}
	} 
	print br,br;
	print hr;
} else {
	print &gen_form();
}
print qq~ <center><a href="http://rousse.pm.org/sasacct/" target="_blank"><img border="0" src="$logopath/poweredbysa.gif"></a></center>
~
;
print end_html();
#end html

#Function generating input form

sub gen_form{
	return startform( -method => 'POST'),
	center,p({class=>"title"},'<b>Start Date [YYYY/MM/DD]</b>'),
	popup_menu(-class =>'input',-name => 'syear', -values => \@years,-Default=>@years[1]),
	popup_menu(-class =>'input',-name=>'smonth', -values=> \@months, -labels=> \%mlabels),
	popup_menu(-class =>'input',-name => 'sday', -values=> \@days),
	p({class=>"title"},'<b>End Date [YYYY/MM/DD]</b>'),
	popup_menu(-class =>'input',-name => 'eyear', -values => \@years, -Default=>@years[1]),
	popup_menu(-class =>'input',-name=>'emonth', -values => \@months , -labels => \%mlabels),
	popup_menu(-class =>'input',-name => 'eday', -values=> \@days),
	p({class=>"default"}),
	checkbox(-class => "default", -name=>'graph',-label => 'Generate graphics for the selected period'),
	p({class=>"default"}),checkbox(-name=>'bits',-label  => 'Show graph in Bits per Second'),
	p({class=>"default"}),checkbox(-name=>'zoom',-label => 'Zoom the graphic'),
	p({class=>"title"},'<b>[Select IP Address]</b>'),
	p,popup_menu(-class =>'input',-name => 'ip', -values=>\@ips),
	p,submit(-class=>'input',-value => 'Submit'),'&nbsp','&nbsp',
	reset(-class=>'input',-value => 'Reset'),
	endform;
}

#Function summarizing the accounting data from date to date

sub gen_traff{
        my($start,$end,$ip)= @_;
        my %bytes;
        if ($ip eq "All") {
                &gen_traff_all($start,$end);
        }else {
	open(IN,"$rkeys{D}"."$ip") if stat("$rkeys{D}"."$ip");
        my $line = <IN>;
        chop $line;
        while (defined($line)) {
        my ($date,$time,$ip,$in,$out) = split(/\s+/,$line);
        if ($date ge $start && $date le $end ) {
        $bytes{in} += $in;
        $bytes{out} += $out;
                }
        $line = <IN>;
                }
        return $bytes{in},$bytes{out};
        }
}
sub gen_traff_all {
        my($start,$end) =@_;
        my %bytes;
        foreach (@ips){
        open (IN,"$rkeys{D}"."$_") if stat("$rkeys{D}"."$_") ;
        my $line = <IN>;
        chop $line;
        while ( defined($line)) {
        my ($date,$time,$ip,$in,$out) = split(/\s+/,$line);
        if ($date ge $start && $date le $end ) {
        $bytes{in} += $in;
        $bytes{out} += $out;
                }
        $line = <IN>;
                }
        }
        return $bytes{in},$bytes{out};
}
