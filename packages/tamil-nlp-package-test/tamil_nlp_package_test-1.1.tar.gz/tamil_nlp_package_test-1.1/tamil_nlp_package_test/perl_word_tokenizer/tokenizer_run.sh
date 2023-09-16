
perl $setu/bin/sys/common/normalize-tam.pl $1 > normalize_in.txt
perl $setu/bin/sl/tokenizer/tokenizer_indic.pl --lang=tam  --j=no --input=normalize_in.txt

##perl $setu/bin/sl/tokenizer/tokenizer_indic.pl --lang=tam --input=$1
