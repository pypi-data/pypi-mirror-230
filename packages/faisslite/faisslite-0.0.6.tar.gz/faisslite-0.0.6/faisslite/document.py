import re

'''
符合以下四个特征的正文，称为formal正文：
 1）段落是由'\n\n'分割的；或
 2）段落是由'\n\t'分割的；或
 3) 段落是由'\n'分割的；
 3）段落内'\s+'==' '。
'''
def formal(doc, sep='\n\n'):
    pattern = {
        '\n\n': r'\n\s*\n',
        '\n\t': r'\n\s+',
        '\n'  : r'\s*\n'
    }
    paras = re.split(pattern[sep], doc.strip())
    paras = [
        formal(para, sep='\n\t') if sep=='\n\n' else
        formal(para, sep='\n')   if sep=='\n\t' else
        re.sub(r'\s+', ' ', para)
        for para in paras
    ]
    return sep.join(paras)

'''
分割formal正文
'''
def split(doc):
    paras = re.split(r'(\n[\n\t]?)', doc)
    paras.append('')
    return [
        {'text': paras[i], 'sep': paras[i+1]}
        for i in range(0, len(paras), 2)
    ]
