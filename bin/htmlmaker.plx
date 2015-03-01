#!/usr/bin/perl 
my $configfile = '/etc/sasacct.conf'; #edit here if needed

open (CNF,"$configfile");
$host = `hostname`;
my $graphdir;
my %ips;

while (<CNF>) {
    if ($_ =~ /^G/){
        chop $_;
        s/^G://g;
        s/\/$//g;
        $_ = $_."\/";
        $graphdir= $_;
    }
    if ($_ =~ /^L/){
        chop $_;
        s/^L://g;
        my ($ip,@i)=split(/:/,$_);
        $ips{$ip}= \@i if !defined($ips{$ip});
    }
}

if (stat($graphdir)) {
    opendir DIR,$graphdir || die ("Cannot open: $!");
    my @files = readdir(DIR);
    closedir DIR;
    for(@files) {
     if ($_ =~ /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\_\d)*?/){
     s/\.html//g;
     s/\-(day|week|month|year).gif$//g;
     $ips{$_} = '' if !exists($ips{$_});
     }
    }
}

foreach $ip (keys %ips) {
	my $descriptions;
	open(FD,">$graphdir"."$ip.html");
	if ($ips{$ip}[0]){
		$description = $ips{$ip}[0];
	}else {
		$description = $ip;	
    }
    print FD ("
<html>
<head>
<title>::SASacct Traffic Stats for $description::</title>
<meta http-equiv=\"Content-Type\" content=\"text/html\"\; charset=iso-8859-1\">
<meta http-equiv=\"Page-Enter\" content=\"filter: blendtrans(duration=0.5)\">
<meta http-equiv=\"Refresh\" content=\"300\">
<style type=\"text\/css\">
<!--
.title {  font-family:Verdana,Helvetica,Arial,sans-serif; font-size: 12px; font-weight: normal; color: #666666}
.default {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #666666}
.small {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 9.5px; color: #666666}
.negative {  color: #FFFFFF; background-color: #666666; font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 12px}
-->
</style>
</head>
<body bgcolor=\"#FFFFFF\" text=\"#000000\" vlink=\"#666666\" alink=\"#009900\" link=\"#333333\">
<p class=\"title\"><img src=\"salogo.gif\" width=\"52\" height=\"58\" align=\"left\"><b>Traffic
Statistics </b><br>
<span class=\"default\">for host [<b>$description</b>]
</span></p>
<br><hr>
<p class=\"default\"><span class=\"title\"><b>[Daily]</b><br><br>
<img src=\"$ip-day.gif\"></span>
</p>
<p class=\"default\"><span class=\"title\"><b>[Weekly]</b><br><br>
<img src=\"$ip-week.gif\"></span>
</p>
<p class=\"title\"><b>[Monthly]</b></font><br><br>
<img src=\"$ip-month.gif\">
</p>
<p class=\"title\"><b>[Yearly]</b><br><br>
<img src=\"$ip-year.gif\">
<hr>
<span class=\"small\"><em>Generated by <a href=\"http://rousse.pm.org/sasacct\">sasacct</a> using <a href=\"http://ee-staff.ethz.ch/\~oetiker/\">Tobias Oetiker</a>'s RRDTool</span><br><br>
<img src=\"poweredbysa.gif\" align=\"left\">
</body>
</html>"
    );
	close FD;
}

########################
# Generate master index
#
open(INDEX,">$graphdir"."index.html");
$count=1;
print INDEX ("
<html>
<title>::SASacct Traffic::</title>
<head>
<meta http-equiv=\"Content-Type\" content=\"text/html\"\; charset=iso-8859-1\">
<meta http-equiv=\"Page-Enter\" content=\"filter: blendtrans(duration=0.5)\">
<style type=\"text\/css\">
<!--
.title {  font-family: Arial, Helvetica, sans-serif; font-size: 12px; font-weight: normal; color: #666666}
.default {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #666666}
.small {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 9.5px; color: #666666}
.negative {  color: #FFFFFF; background-color: #666666; font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 12px}
-->
</style>
</head>
<body bgcolor=\"#FFFFFF\" text=\"#000000\" link=\"#999999\" vlink=\"#666666\" alink=\"#666600\">
<p class=\"title\"><img src=\"salogo.gif\" width=\"52\" height=\"58\" align=\"left\"><b>Traffic
Statistics </b><br>
<span class=\"default\">for router [<b>$host</b>]
</span></p>
<br>
<hr>
"
);

foreach $ip(keys %ips) {
 if ($count%2 !=0 ){
    print INDEX ("<tr><td><a href=\"$ip.html\"><img src=\"$ip-day.gif\" border=\"0\"></a></td>\n");
    $count++;
    } else { 
    print INDEX ("<td><right><a href=\"$ip.html\" border=\"0\"><img src=\"$ip-day.gif\" border=\"0\"></a></right></td></tr>\n");
	$count++;
	}
}
print INDEX ("</table>
<hr><span class=\"small\">Generated by <a href=\"http://rousse.pm.org/sasacct\">sasacct</a> using <a href=\"http://ee-staff.ethz.ch/\~oetiker/\">Tobias Oetiker</a>\'s RRDTool</span><br><br>
<img src=\"poweredbysa.gif\">
</body>
</html>");
close INDEX;