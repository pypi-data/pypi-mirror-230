from argparse import ArgumentParser
from collections import OrderedDict
import sys
import re
import os.path
# import logger as log
import tamil_nlp_package_test.logger as log

acr_hash = {}
count = 0


def get_keylength(v):
    key, values = v
    return len(key), values[0]


def acr_func(file):
    global count
    fp1 = open(file, encoding="UTF-8")  # Open file on read mode -- input file
    lines = fp1.read().split("\n")  # Create a list containing all lines
    fp1.close()  # Close file
    for line in lines:
        line.strip()
        if (line == ""):
            continue
        acr_hash[line] = "____ACRHASH____" + str(count) + "____ACRHASH____"
        log.logging.info(
            "Saving accronym hash key=|%s|, value=|%s|" % (line, "____ACRHASH____" + str(count) + "____ACRHASH____"))
        count = count + 1


# parser = ArgumentParser(description='This script will tokenize input file sentence wise\n\r'+
# 						"How to Run?\n" +
# 						"python3 " + sys.argv[0] + " -i=in.txt" + "-acr=tam.txt"
# 						)
# parser.add_argument("-i", "--input", dest="inputfile",
#                     help="provide input file name",required=True)
# parser.add_argument("-a", "--acr", dest="acrfile",
#                     help="provide acr file name like tam.acr,required=False")

# args = parser.parse_args()
# inputfile = args.inputfile
# acrfile = args.acrfile
def tokenize(input_string):
    global count
    out_lines = []
    url_hash = {}
    acrfile = os.path.dirname(__file__) + "\\tam.acr"
    string_exists = bool(input_string)
    # file_exists = os.path.exists(inputfile)
    if (not string_exists):
        # print("Given %s file does not exists" % (inputfile))
        print("Given string is empty")
        exit()
    else:
        # open file using open file mode
        log.logging.info("got input string")
        # fp = open(inputfile, encoding="UTF-8")  # Open file on read mode -- input file
        # inlines = fp.read().split("\n")  # Create a list containing all lines
        # fp.close()  # Close file
        inlines = input_string.split("\n")

        acr_file_exists = os.path.exists(acrfile)
        if (acr_file_exists):
            log.logging.info("Acronym file exists, going to hash the acronyms")
            acr_func(acrfile)
            acr_hash_od = OrderedDict(sorted(acr_hash.items(), key=get_keylength, reverse=True))
            # print(acr_hash)
            line_no = 1
        for l in inlines:
            # print(l)
            # l.strip()
            log.logging.debug("Reading inputfile line by line, current line=|%s|" % (l))

            if (l == ""):
                out_lines.append(l + "____ORIGINALLINEBREAK____")
                # print(l)https://www.eenadu.net/telugu-news/ts-top-news/general/2601/123108108
                continue

            # handle urls
            # urls = re.findall(r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', l)
            # urls = re.findall(r'(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])', l) #https://stackoverflow.com/questions/6038061/regular-expression-to-find-urls-within-a-string
            urls = re.findall(
                r'(?:(?:https?:\/\/|ftp:\/\/|:file:\/\/|www)+[a-zA-Z0-9.\-]+\.[a-zA-Z]+\/?[a-zA-Z0-9_.\-]*)', l)
            # print(urls)
            for u in urls:
                log.logging.info("Found url in current line url=|%s|" % (u))

                val = "____ACRHASH____" + str(count) + "____ACRHASH____"
                url_hash[val] = u
                log.logging.info("Saving url in acr hash with key=|%s|, value=|%s" % (u, val))

                l = re.sub(r'' + u, r'' + "____ACRHASH____" + str(count) + "____ACRHASH____", l)
                log.logging.debug("Current line=|%s| after url substituion=" % (l))
                count = count + 1

            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', l)
            for e in emails:
                log.logging.info("Found email in current line email=|%s|" % (e))

                val = "____ACRHASH____" + str(count) + "____ACRHASH____"
                url_hash[val] = u
                log.logging.info("Saving email in acr hash with key=|%s|, value=|%s" % (e, val))

                l = re.sub(r'' + e, r'' + "____ACRHASH____" + str(count) + "____ACRHASH____", l)
                log.logging.debug("Current line=|%s| after email substituion" % (l))
                count = count + 1

            acr_hash_od = OrderedDict(sorted(acr_hash.items(), key=get_keylength, reverse=True))
            for k in acr_hash_od:
                # print(l)
                l = re.sub(r' ' + re.escape(k), r' ' + acr_hash_od[k], l)

            log.logging.debug("Current line after acr hash substituion from acr file line=|%s|" % (l))

            l = re.sub(r'(\.){3,3}', r'__ELLIPSE3__', l)
            log.logging.debug("Current line=|%s| after ... substituion" % (l))

            l = re.sub(r'(\.){2,2}', r'__ELLIPSE2__', l)
            log.logging.debug("Current line=|%s| after .. substituion" % (l))

            # l = "<S> " + l
            l = re.sub(r'([^0-9])([\.?\u06D4\u061F\u0964\!\|]+)( [\"\'])*([^\u2160-\u217F])', r'\1\2</S><S>\3\4', l)
            log.logging.debug("Current line=|%s| after actual dot substituion with sentence boundary" % (l))

            if (not re.search(r'<\/S><S>', l)):
                out_lines.append(l + "____ORIGINALLINEBREAK____")
            else:
                out_lines.append(l)
            line_no = line_no + 1
    # print(l)

    inv_hash = {v: k for k, v in acr_hash_od.items()}
    # print(inv_hash)
    # out_arr = out_lines
    all_hash = inv_hash
    all_hash.update(url_hash)
    i = 0
    for key in all_hash:
        i = 0
        log.logging.debug("Current key=|%s|, value=|%s|" % (key, inv_hash[key]))
        for o in out_lines:
            # print("key|" + key + "|str|" + o, inv_hash[key])
            log.logging.debug("Before substitution with actual values, current key=|%s|, value=|%s|, line=|%s|" % (
                key, inv_hash[key], o))
            o = re.sub(r'' + key, r'' + inv_hash[key], o)
            log.logging.debug("After substitution with actual values, current key=|%s|, value=|%s|, line=|%s|" % (
                key, inv_hash[key], o))
            o = re.sub(r'__ELLIPSE3__', r'...', o)
            o = re.sub(r'__ELLIPSE2__', r'..', o)
            o = re.sub(r'</S><S> ?', r'\n', o)
            out_lines[i] = o
            # print(o)
            i = i + 1

    out_str = "".join(out_lines)
    out_str = re.sub(r'____ORIGINALLINEBREAK____', '\n', out_str)
    return out_str
    # nf = open('res.txt', 'w', encoding="UTF-8")
    # nf.write(out_str)
    # nf.close()
# print(out_str)
