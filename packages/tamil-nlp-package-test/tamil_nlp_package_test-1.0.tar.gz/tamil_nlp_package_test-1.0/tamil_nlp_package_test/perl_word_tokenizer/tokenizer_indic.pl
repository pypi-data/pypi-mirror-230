#!/usr/bin/perl
use Getopt::Long;
use File::Basename;

GetOptions('help!'=>\$help, 'lang=s'=>\$lang, 'str_input=s'=>\$str_input, 'input=s'=>\$input, 'output:s'=>\$output, 'version'=>\$ver, 'jflag:s'=>\$jflag);
print "Unprocessed by Getopt::Long\n" if $ARGV[0];
foreach (@ARGV) {
       print "$_\n";
       exit(0);
}

if($help eq 1) {
	print "usage :\nperl  tokenizer_indic.pl -l=hin -i=input-file -o=output \n\n";
	print " -l, --lang=[hin|tel|...]	: select the language 3 letter code (ISO-639)\n";
	print " -s, --str_input=<input-string>	: give input string\n";
	print " -i, --input=<input-file>	: give input file\n";
	print " -o, --output=<output-file>	: give output file\n";
	print " -j, --jflag=[yes|no]		: give input to print -JOIN in between multiwords. default is yes\n";
	print "Report bugs to <rashid101b\@gmail.com>\n";
        exit(0);
}

if($ver eq 1) {
        print "tokenizer-indic version 1.8 \n";
        exit(0);
}

# for ~/Desktop/ or ~/myinput/ directory issue fix
$home = $ENV{"HOME"};
$input =~ s/^~/$home/;
$output =~ s/^~/$home/;

use Cwd 'abs_path';
$path = dirname($0);
$path = abs_path($path);

# Acronym file path based on language
$acr_file = $path."/data/".$lang.".acr";

#print "Path: $path\n";
#print "Input String: $str_input\n";
#print "Input File: $input\n";
#print "Output: $output\n";
#print "Acronym File : $acr_file\n";
#print "JOIN FLAG : $jflag\n";

# tokenizer-indic lib
require "$path/lib/tokenizer.pl";

#binmode (STDOUT, ":utf8");
#binmode (STDIN, ":utf8");
sub tokenizer_indic {
	my ($lang, $str_input, $input, $output) = @_;

        if ($output ne "") {
            open (OUTFILE, ">$output") or die "$!";
        }

	if ($str_input ne "" and lc($lang) ne "") {
		my $tokenize_str = &sentence_mark($lang, $str_input, $acr_file, $jflag);
		my $final_ssf = &token_split($tokenize_str);
		if ($output ne "") {
			binmode (OUTFILE, ":utf8");
			print OUTFILE $final_ssf;
		}
		else {
			binmode (STDOUT, ":utf8");
			print $final_ssf;
		}
	}
	elsif ($input ne "" and lc($lang) ne "") {
		# Input file open if input string is not specified
		open (INFILE, "<utf8", $input) or die "$!";
		#$line = join(" ", grep{ chomp $_; } <INFILE>);
		my $sent_str = "";
		my $id = 1;
		while ($line = <INFILE>) {
			if($id == 1 ) {
				$url = $line;
				$url =~s/OTOT//g;
			} elsif($id == 2) {
				$url .=$line;
				$url =~s/\n/\t/;
			}
			else {
				$orig_line = $line;
				$tokenize_str = &sentence_mark($lang, $line, $acr_file, $jflag);
				$conlu_format = &token_split($tokenize_str,$orig_line,$id-2, $url);
				$token_conlu_format .= $conlu_format;
			}
				$id = $id + 1;
		#$line = join("",  <INFILE>);
		#if ($line !~ m/^$/) {
		#	$tokenize_str = &sentence_mark($lang, $line, $acr_file, $jflag);
		#	$sent_str = $sent_str.$tokenize_str;
		#	$line_str = $line_str.$line;
		#}
		}
		if ($output ne "") {
			binmode (OUTFILE, ":utf8");
                        print OUTFILE $token_conlu_format;
                }
                else {
                        print $token_conlu_format;
                }

	}
	else {
		print "\nOptions Missing\n";
		print "usage :\nperl  $0 -l=hin -i=input-file -o=output \n\n";
	}
	print "Completed.";

}
&tokenizer_indic($lang, $str_input, $input, $output);

