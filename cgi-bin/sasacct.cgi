#!/usr/bin/perl 
use strict;

use CGI::Pretty qw (:all *table);
use CGI::Carp qw(fatalsToBrowser);
use CGI::Session;
use File::Basename;
use Time::Local; 
use Time::localtime qw (:FIELDS);

my $page;
my $configfile = "/etc/sasacct.conf";
my $logopath = '/sasacct';
my $usersfile = '/etc/sasacct.users';

#cgi states
my %states = (
	display => \&display,
    gprint => \&gprint,
	init => \&init,
	login => \&login,
	login_failed => \&login_failed,
	logout => \&logout,
	utilization_form => \&utilization_form,
	utilization => \&utilization
);

###############################
# main 

my $cgi = new CGI;
my $session = new CGI::Session(undef, $cgi, {Directory=>'/tmp'});
my $cookie = $cgi->cookie( -name=> 'CGISESSID' ,-value => $session->id );


_init_session($session,$cgi,$usersfile);

if ( $session->param("~login-trials") >= 3 ) {
    $page = 'login_failed';

    print_head();
    $states{$page}->();
    print_foot();

    exit(0);
}

unless( $session->param("~logged-in") ) {
    $page = 'login';

    print_head();
    $states{$page}->();
    print_foot();

    exit(0);
}

#read config 
my ($local,$rkeys) = _parse_conf($configfile);

#ip addresses wich user can see
my $ips = _get_ipaddr();push @$ips,"All"; 

#default page after auth
if ($cgi->param('state') eq 'gprint') {
	$states{'gprint'}->($ips);
} elsif ($cgi->param('state')) {
	$page = $cgi->param('state');
} else {
	$page = 'init';
}

print_head();
if ($states{$page}){
	$states{$page}->();
}
print_foot();

########################################
# functions
sub init {
	_form();
}

sub logout {
	$session->delete();
	my $myself = $cgi->url(-relative);
	$states{'login'}->();
}

sub utilization_form {
	my $myself = $cgi->url(-relative);
	my $link = "<p class=\"small\"><a href=\"$myself?state=init\">Main Page&nbsp&nbsp</a>";
	$link = $link." <a href=\"$myself?state=logout\">Logout</a>";

	print table,Tr,td([$link]);

	print startform( -method => 'POST'),
	start_table({border => 0,class=>'default'}),
    Tr,
	td({class=>'b_title',align=>'left'}),"IP_ADDRESS",
	td({class=>'default',align=>'right'}),
	popup_menu(-class =>'input',-name => 'ip', -values=>$ips),
    Tr,
	td,
	td({class=>'default',align=>'right'}),
	submit(-class=>'input',-NAME =>'state',-value => 'utilization'),'&nbsp','&nbsp',
    reset(-class=>'input',-value => 'reset'),
	end_table,
    endform;

}

sub utilization {
	my $unix_time = time();
	my $day = $unix_time - 86000;
	my $week = $unix_time - 604800;
	my $month = $unix_time - 2600640;
	my $year = $unix_time - 31557600;
	my $ip = param('ip');

	my $myself = $cgi->url(-relative);
	my $fpathrrd = $$rkeys{D}.$ip.".rrd";

	#print $fpathrrd;

	$states{'utilization_form'}->();

	if (-f $fpathrrd) {
		print br,start_table({border => 0,class=>'default'}),
		Tr,td({class=>'b_title',align=>'center'}),"[Daily]",
		td({class=>'b_title',align=>'center'}),"[Weekly]",
		Tr,
		td,img({-src => "$myself?state=gprint\&utcstart=$day\&utcend=$unix_time\&ip=$ip\&bits=0\&zoom=0"}),
		td,img({-src => "$myself?state=gprint\&utcstart=$week\&utcend=$unix_time\&ip=$ip\&bits=0\&zoom=0"}),
		Tr,td({class=>'b_title',align=>'center'}),"[Monthly]",
		td({class=>'b_title',align=>'center'}),"[Yearly]",
		Tr,
		td,img({-src => "$myself?state=gprint\&utcstart=$month\&utcend=$unix_time\&ip=$ip\&bits=0\&zoom=0"}),
		td,img({-src => "$myself?state=gprint\&utcstart=$year\&utcend=$unix_time\&ip=$ip\&bits=0\&zoom=0"}),
		end_table;
	}

}

sub _form {
  	my @years = (2003,2004,2005,2006,2007);

    my %mlabels= (
    '01' => 'Jan','02' => 'Feb','03' => 'Mar',
    '04' => 'Apr','05' => 'May','06' => 'Jun',
    '07' => 'Jul','08' => 'Aug','09' => 'Sep',
    '10' => 'Oct','11' => 'Nov','12' => 'Dec'
    );

    my @months =(
    '01','02','03','04','05','06',
    '07','08','09','10','11','12'
    );

    my @days = qw (
    01 02 03 04 05 06 07 08 09 10 11 12 13 14 15
    16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
	);

	my $now = localtime(); # with Time::localtime gives us tm_* variables

	#links
	my $myself = url(-relative);
	my $link = "<P CLASS=\"small\"><A HREF=\"$myself?state=utilization_form\">Utilization</A>";
	my $link = $link." <A HREF=\"$myself?state=logout\">Logout</A>";
	print $link,br,br;


	return print startform( -method => 'POST'),
	start_table({border => 0,-class => 'default',-cellSpacing => '0', -cellPadding => '3',
		-style => 'BORDER-COLAPSE: colapse',-borderColor => '#999999'}),
	Tr,td({class=>'b_title',align=>'left'}),"START_DATE",
    td({class=>'default',align=>'right',valign=>'middle'}),
	popup_menu(-class =>'input',-name => 'syear', -values => \@years,-default=>($tm_year+1900)),
    popup_menu(-class =>'input',-name=>'smonth', -values=> \@months, -labels=> \%mlabels, -default=>$months[$tm_mon]),
    popup_menu(-class =>'input',-name => 'sday', -values=> \@days),
	Tr,td({class=>'b_title',align=>'left'}),"END_DATE",
	td({class=>'default',align=>'right',valign=>'middle'}),
    popup_menu(-class =>'input',-name => 'eyear', -values => \@years, -default=>($tm_year+1900)),
    popup_menu(-class =>'input',-name=>'emonth', -values => \@months , -labels => \%mlabels, -default=>$months[$tm_mon]),
    popup_menu(-class =>'input',-name => 'eday', -values=> \@days, -default => $tm_mday),
	Tr,td({class=>'b_title',align=>'left'}),"IP_ADDRESS",
	td({class=>'default',align=>'right',valign=>'middle'}),
	popup_menu(-class =>'input',-name => 'ip', -values=>$ips),
	Tr,td({class=>'b_title',align=>'left'}),"GRAPHIC",
    td({class=>'small',valign=>'middle',align=>'right'}),
	checkbox(-class => "default", -name=>'graph',-label => 'SHOW'),
    checkbox(-name=>'bits',-label  => 'BITS'),
    checkbox(-name=>'zoom',-label => 'ZOOM'),
	Tr,td({class=>'b_title',align=>'left'}),
    td({class=>'default',align=>'right',valign=>'middle'}),
    submit(-class=>'input',-NAME =>'state',-value => 'display'),'&nbsp','&nbsp',
    reset(-class=>'input',-value => 'reset'),
	end_table,
    endform;
}

sub display {
	 
	my $bits = param('bits');
    my $zoom = param('zoom');
    my $startdate = (param('syear').param('smonth').param('sday'));
    my $enddate = (param('eyear').param('emonth').param('eday'));
    my $ip = param('ip');
    my $sdateformated = (param('sday').'-'.param('smonth').'-'.param('syear'));
    my $edateformated = (param('eday').'-'.param('emonth').'-'.param('eyear'));
    my $dograph = param('graph');
    my $myself = $cgi->url(-relative);

	_form();
	
	my ($in,$out) = _gen_traff($startdate,$enddate,$ips,$ip);

	if ($in && $out){
        print 
        p({class=>"default"},
        "Total traffic from <b>$sdateformated</b> to <b>$edateformated</b> 
		for <a href=\"$myself?state=utilization&ip=$ip\">$ip ($$local{$ip}[0])</A>"
        );

        my $total = $in+$out;
        my $totalmb = sprintf("%.3f", $total/1024/1024);
        
		print 
		start_table(
		{border => 1,-class => 'default',-cellSpacing => '0', -cellPadding => '3',
		-style => 'BORDER-COLAPSE: colapse',-borderColor => '#999999'}),
        Tr(),
        td({class=>'th',align=>'middle'},
		['IP_ADDRESS','INPUT_TRAFFIC [bytes]','OUTPUT_TRAFFIC [bytes]', 'TOTAL [bytes]','TOTAL [MBytes]']),
        Tr({-valign =>"middle",-align =>"middle"}),
        td({class=>'default',align=>'left'},
		["$ip","$in","$out","$total","$totalmb"]),
		end_table;


        if ($dograph eq 'on' && $ip ne "All" ) {
            my $utcstart  = timelocal('00','00','00',param('sday'),param('smonth')-1,param('syear'));
            my $utcend = timelocal('00','00','00',param('eday'),param('emonth')-1,param('eyear'));

            ($utcend = $utcstart + 86000) if ($utcstart == $utcend);
            ($bits eq "on") ? ($bits = 1) : ($bits = 0);
            ($zoom eq "on") ? ($zoom = 1): ($zoom = 0);

            print br,br;
            if ($utcstart < $utcend ) {
            print img(
                {-src => "$myself?state=gprint\&utcstart=$utcstart\&utcend=$utcend\&ip=$ip\&bits=$bits\&zoom=$zoom"});
            }
            print br,br;
        }
    }
    return;
}

sub _get_ipaddr {
    my $profile = $session->param("~profile");
    my $users = _parse_users($usersfile);
	my @ips = sort split (/,/,$$users{$profile->{username}}->{'ip'});
	

	#magic keyword All in users.file
	#can see the traffic for all ip addresses

	if ($ips[0] eq "All") {
		my @all;

		if ( -d $$rkeys{D}) {
    		opendir DIR,$$rkeys{D} 
				|| croak ("Cannot open: $!");
    		my @files = readdir(DIR);
    		for(@files) {
       		 if ($_ =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\_\d+)*?$/
       		     && $_ !~ /rrd/g){
       		     push @all,$_;
       		 }
    		}
			@ips = sort @all;
			closedir(DIR);
		}
	}
    return \@ips;
}

sub _parse_conf {
    my ($configfile) = @_;
    my (%local,%rkeys);
    open(CNF,"$configfile")
        || croak ("Can't open $configfile: $!");

    while(<CNF>) {
        chomp;
        if ($_ =~ /^D/ && !exists($rkeys{D})) {
            s/^D://g;
            s/\/$//g;
            $_ = $_."\/";
            $rkeys{D} = $_;
        }
        if ($_ =~ /^L/ ){
            s/^L://g;
            my ($ip,@i)=split(/:/,$_);
            $local{$ip}= \@i if !defined($local{$ip});
        }
     }
    close CNF;
    return (\%local,\%rkeys);
}

sub _init_session {
	my ($session, $cgi) = @_;
    if ( $session->param("~logged-in") ) {
        return 1;
    }
    my $lg_name = $cgi->param("user") or return;
    my $lg_psswd= $cgi->param("password") or return;

    if ( my $profile = _check_password($lg_name, $lg_psswd,$usersfile) ) {
        $session->param("~profile", $profile);
        $session->param("~logged-in", 1);
        $session->clear(["~login-trials"]);
        return 1;
    }
    my $trials = $session->param("~login-trials") || 0;
    return $session->param("~login-trials", ++$trials);
}

sub _check_password {
    my ($u,$p,$usersfile) = @_;
    my $i;
    my $users = _parse_users($usersfile);
    if ($$users{$u}->{password} eq $p) {
        my $p_mask = "x" . length($p);
        return { username=>$u, password=>$p_mask, ip=> $i};
    }
    return undef;
}

sub _parse_users {
    my ($p) = @_;
    my %u;
    open(U,"<$p")
        || croak("missing users file");
    while (<U>) {
        next if $_ =~ /^#/g;
        next if $_ =~ /^\s+/g;
        /(.*)\:(.*)\:(.*)/;
        $u{$1}->{password} = $2;
        $u{$1}->{ip} = $3;
    }
    return \%u;
}

sub login {
    return print startform(-method =>'POST'),
    start_table({border => 1,-class => 'default',-cellSpacing => '0', -cellPadding => '3',
        -style => 'BORDER-COLAPSE: colapse',-borderColor => '#999999'}),
    Tr,td,
    start_table({border => 0,-class => 'default',-cellSpacing => '0', -cellPadding => '3',
        -style => 'BORDER-COLAPSE: colapse',-borderColor => '#999999'}),
    Tr,td,p({class=>"title"},'<b>Username</b>'),td,textfield(-name=>'user'),br,
    Tr,td,p({class=>"title"},'<b>Password</b> '),td,input({-name=>'password', -type=>'password'}),br,
    Tr({-valign =>"middle",-align =>"middle"}),td,td,
	submit(-class=>'input',-value => 'submit'),'&nbsp','&nbsp',
    reset(-class=>'input',-value => 'reset'),end_table,end_table,
    endform;
}

sub login_failed {
  print p('You failed 3 times to log in.<br>
            Your session is <b>logged</b>.'
	);

}

sub print_head {

print $cgi->header(-cookie => $cookie);

print start_html(
-title => 'SASacct Accounting Statistics',
-head=>meta({-http_equiv => 'Page-enter',-content=>'filter: blendtrans(duration=0.5)'}),
-style => { 'code' => 
'.title {font-family:Verdana,Helvetica,Arial,sans-serif; font-size: 12px; font-weight: normal; color: #666666}
.b_title {font-family:Verdana,Helvetica,Arial,sans-serif; font-size: 12px; font-weight: bold; color: #666666}
.th {font-family:Verdana,Helvetica,Arial,sans-serif,color: #FFFFFF;font-size:12px;font-weight:bold}
.default {font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000}
.small {font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 10px; color: #666666}
.select {background: #ffffff; FONT-FAMILY: verdana; FONT-SIZE: 12pt; border: 1px solid black; padding: 2px;color: #000000}
.negative {color: #FFFFFF; background-color: #666666; font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 12px}'
},
-bgcolor => '#FFFFFF', -text =>'#666666', -vlink =>'#666666', -alink =>'#009900', -link =>'#333333'
);
print center,img({src=>"$logopath/salogo.gif"}),
p({-class=>"title"},'<b>[Traffic Statistics]</b>');
print hr;

}

sub print_foot {
print hr,br;
print qq~ <a href="http://rousse.pm.org/sasacct/" target="_blank"><img border="0" src="$logopath/poweredbysa.gif"></a>
~
;
print end_html();
}

sub gprint {
    my $utcstart = $cgi->param('utcstart');
    my $utcend = $cgi->param('utcend');
    my $ip = $cgi->param('ip');
    my $bits= $cgi->param('bits');
    my $zoom = $cgi->param('zoom');

	my $match = 0; 

	#stupid search	
	for(@{_get_ipaddr()}) {  
		if ($ip =~ /$_/) { 
			$match = 1;
			last;
		}
	}

	return if ($match == 0);

	my $fpathrrd = $$rkeys{'D'}."$ip".".rrd";
    my (@header_str,@def_str,@data_str,@comment_str);

    print $cgi->header(
        -type=>'image/png',
        -expires => 'now',
        -Cache-Control => 'no-cache'
    );

    @header_str = (
    "--imgformat","PNG",
    "--start","$utcstart",
    "--end","$utcend",
    );
    if ($zoom == 1) {
        push @header_str,("-w","600","-h","150");
    }
    if ($bits == 1){
    @def_str = (
    "DEF:indatabits=$fpathrrd:in:AVERAGE",
    "DEF:outdatabits=$fpathrrd:out:AVERAGE",
    "CDEF:indata=indatabits,8,*",
    "CDEF:outdata=outdatabits,8,*",
    "CDEF:averagein=indata,UN,0,indata,IF",
    "CDEF:averageout=outdata,UN,0,outdata,IF"
    );
    push @header_str,(
    "--vertical-label",
    "Bits per second","--base","1000",
    "--units-exponent","3"
    );
    }else {
    @def_str =(
    "DEF:indatabytes=$fpathrrd:in:AVERAGE",
    "DEF:outdatabytes=$fpathrrd:out:AVERAGE",
    "CDEF:indata=indatabytes",
    "CDEF:outdata=outdatabytes",
    "CDEF:averagein=indatabytes,UN,0,indatabytes,IF",
    "CDEF:averageout=outdatabytes,UN,0,outdatabytes,IF",
    );
    push @header_str,("--vertical-label","Bytes per second");
    }

    @data_str = ("AREA:averagein#00CC00:In",
    "GPRINT:indata:AVERAGE:Avg\\:%8.2lf%s",
    "GPRINT:indata:MIN:Min\\:%8.2lf%s",
    "GPRINT:indata:MAX:Max\\:%8.2lf%s",
	"GPRINT:indata:LAST:Current\\:%8.2lf%s\\n",
    "LINE1:averageout#0000FF:Out",
    "GPRINT:outdata:AVERAGE:Avg\\:%8.2lf%s",
    "GPRINT:outdata:MIN:Min\\:%8.2lf%s",
    "GPRINT:outdata:MAX:Max\\:%8.2lf%s",
    "GPRINT:outdata:LAST:Current\\:%8.2lf%s\\n"
    );
	@comment_str=("COMMENT:Generated by sasacct http\\://rousse.pm.org/sasacct \\c");
    require 'RRDs.pm';
    #don't buffer output
    $|=1;
    RRDs::graph("-",@header_str,@def_str,@data_str,@comment_str);
	
	my $ERROR = $RRDs::error;
	 if ($ERROR){
	       print("$ERROR\n");
	  }
    exit;
}

sub _gen_traff {

    my($start,$end,$ips,$ip)= @_;
    my %bytes;

    if ($ip eq "All") {
        _gen_traff_all($start,$end,$ips);
    } else {
        open(IN,"$$rkeys{D}"."$ip") if stat("$$rkeys{D}"."$ip");
        while (<IN>) {
            my ($date,$time,$_ip,$in,$out) = split(/\s+/,$_);
            if ($date ge $start && $date le $end ) {
                $bytes{in} += $in;
                $bytes{out} += $out;
            }
        }
		close IN;
        return $bytes{in},$bytes{out};
        }
}

sub _gen_traff_all {

    my($start,$end,$ips) = @_;
    my %bytes;

    foreach (@$ips) {
        open (IN,"$$rkeys{D}"."$_") if stat("$$rkeys{D}"."$_") ;
        my $ln = <IN>;
        while ($ln) {
            my ($date,$time,$ip,$in,$out) = split(/\s+/,$ln);
                if ($date ge $start && $date le $end ) {
                    $bytes{in} += $in;
                    $bytes{out} += $out;
                }
            $ln = <IN>;
        }
    }
    return $bytes{in},$bytes{out};
}

