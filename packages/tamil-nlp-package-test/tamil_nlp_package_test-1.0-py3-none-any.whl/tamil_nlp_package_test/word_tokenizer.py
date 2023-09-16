import subprocess


def tokenize(lang, input_file, output_file):
    subprocess.Popen(
        ['perl', 'perl_word_tokenizer/tokenizer_indic.pl', f"-l={lang}", f"-i={input_file}", f"-o={output_file}.txt"],
        stdout=subprocess.PIPE)
