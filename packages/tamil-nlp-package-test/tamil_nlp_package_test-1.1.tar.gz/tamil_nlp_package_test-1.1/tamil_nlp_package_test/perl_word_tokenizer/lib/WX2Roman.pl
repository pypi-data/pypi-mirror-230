
use Encode;
#while ($line=<>){
sub wx2roman {
	$line = $_[0];
	$line=~s/A/ā/g;
		#$line=~s/A/\\={a}/g;
		$line=~s/e([^V])/ē\1/g;
		#$line=~s/e([^V])/\\={e}$1/g;
		$line=~s/eV/e/g;
		$line=~s/O/av/g;
		$line=~s/o([^V])/ō\1/g;
		#$line=~s/o([^V])/\\={o}$1/g;
		$line=~s/oV/o/g;
		$line=~s/I/ī/g;
		#$line=~s/I/\\={\\i}$1/g;
		$line=~s/U/ū/g;
		#$line=~s/U/\\={u}$1/g;
		$line=~s/E/ay/g;
#		$line=~s/H/H/g;
		$line=~s/f/ṅ/g;
		$line=~s/F/ñ/g;
		#$line=~s/f/\\\.{n}/g;
		$line=~s/t/ṭ/g;
		$line=~s/T/ṭh/g;
		$line=~s/d/ḍ/g;
		$line=~s/D/ḍh/g;
		#$line=~s/t/\\d{t}/g;
		#$line=~s/T/\\d{t}h/g;
		#$line=~s/d([^\{])/\\d{d}$1/g;
		#$line=~s/D([^\{])/\\d{d}h$1/g;

		$line=~s/c/c/g;
		$line=~s/C/ch/g;
		$line=~s/j/j/g;
		$line=~s/J/jh/g;
		$line=~s/q/ṙ/g;
		$line=~s/Q/ṝ/g;
		$line=~s/H/Ɂ/g;
		$line=~s/lV/ɫ/g;


		$line=~s/k/k/g;
		$line=~s/K/kh/g;
		$line=~s/g/g/g;
		$line=~s/G/gh/g;

		$line=~s/p/p/g;
		$line=~s/P/ph/g;
		$line=~s/b/b/g;
		$line=~s/B/bh/g;
		$line=~s/m/m/g;

		$line=~s/w/t/g;
		$line=~s/W/th/g;
		$line=~s/x/d/g;
		$line=~s/X/dh/g;
		$line=~s/n/n/g;

		$line=~s/rY/ṟ/g;
		#$line=~s/rY/\\b{r}/g;
		$line=~s/nY/ṉ/g;
		#$line=~s/nY/\\b{n}/g;
		$line=~s/N/ṇ/g;
		#$line=~s/N/\\d{n}/g;
		#$line=~s/lYY/ḻ/g;
		$line=~s/lYY/ẓ/g;
		$line=~s/lY/ḷ/g;
		$line=~s/s/s/g;
        $line=~s/R/ṣ/g;
        $line=~s/S/ś/g;
        $line=~s/v/w/g;
        $line=~s/y/y/g;
		return $line;
		#print "$line";
	}

1;
