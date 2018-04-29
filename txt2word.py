import re, sys, os
from collections import defaultdict
from codecs import BOM_UTF8, BOM_UTF16_BE, BOM_UTF16_LE, BOM_UTF32_BE, BOM_UTF32_LE

'''
Summary word numbers of txt or srt file. 

Usage:  python txt2word.py 
        python txt2word.py word_summary .txt,.srt ./

You can give fileout name, prefix and search_path.
'''

def check_text_format(filein):
    
    BOMS = (
        (BOM_UTF8, "UTF-8"),
        (BOM_UTF32_BE, "UTF-32-BE"),
        (BOM_UTF32_LE, "UTF-32-LE"),
        (BOM_UTF16_BE, "UTF-16-BE"),
        (BOM_UTF16_LE, "UTF-16-LE"),
    )

    data = open(filein, 'rb').read(64)
    
    for bom, encoding in BOMS:
        if data.startswith(bom):
            return encoding
    return ""

def txt2word(filein):
    '''
    store the senstence which the word apperate at the first time.
    '''
    
    re_pattern = re.compile(r'[a-zA-z]+')
    
    data = {}
    
    file_encoding = check_text_format(filein)
    if not file_encoding:
        raise IOError("Can't decode {}".format(filein))

    for l in open(filein, encoding=file_encoding):
        for match in re_pattern.finditer(l):
            word = match.group()
            start, end = match.span()
            if start != 0 and l[start-1] == "'":
                continue
            if end != len(l) - 1 and l[end] == "'":
                continue
            word = word.lower()
            if len(word) < 3:
                continue
            try:
                data[word][0] += 1
            except:
                data[word] = [1, l.strip()]
    return data
    
def iter_combine_dict(datas = []):
    
    '''
    The first element store the total num.
    '''
    
    def combine_dict(datas=[]):
        data_num = len(datas)
        r = {}
        for i, data in enumerate(datas):
            for k, (v, senstence) in data.items():
                try:
                    r[k][i+1] = v
                except:
                    r[k] = [0] * (data_num+2)
                    r[k][i+1] = v
                    r[k][data_num+1] = senstence
        for k, v in r.items():
            v[0] = sum(v[1:(data_num+1)])
        return r
    
    r = combine_dict(datas)
    return sorted(r.items(), key=lambda x: x[0])
    #return sorted(r.items(), key=lambda x: x[1][0])

def get_fileins(dir="", prefixs=[]):
    dir = os.path.abspath(dir)
    r = []
    for (path, dirs, files) in os.walk(dir):
        for filename in files:
            if prefixs:
                file_prefixs = os.path.splitext(filename)[1]
                if file_prefix not in prefixs:
                    continue
            r.append(os.path.join(path, filename))
    return r


try:
    fileout = sys.argv[1]
except:
    fileout = "word_summary"
try:
    prefixs = sys.argv[2].split(",")
except:
    prefixs = [".txt", ".srt"]
try:
    path = sys.argv[3]
except:
    path = "./"

fileins = get_fileins(path)


datas = []
for filein in fileins:
    datas.append(txt2word(filein))

with open(fileout, 'w') as o:
    for i, filein in enumerate(fileins):
        o.write("#{}\t{}\n".format(i, filein))
    o.write('{:<15}total\t'.format("word") + "\t".join([str(i) for i in range(len(fileins))]) + "\texample\n")
    for word, time_list in iter_combine_dict(datas):
        o.write('{:<15}'.format(word) + '\t'.join([str(i) for i in time_list]) +"\n")

    
            
