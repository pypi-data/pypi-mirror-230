# About
一个用于中文文本向量化和相似度搜索的Python包。它可以将中文段落表征为向量矩阵,并构建向量搜索索引,用于快速准确检索文本中的相似句子。

# Install
`$ pip3 install -U faisslite`

# Director 
+ faisslite 
    + document.py
    + Faiss.py

## document.py
对输入文本进行规范化处理，并将输入文本拆分成段落。
- formal函数
  实现文本的预处理功能，输入原始文本,可以输出规范化了格式的文本内容。
- split函数
  将文本拆分为由文本段落和分隔符构成的字典，为后续向量化处理文本提供了基础。

## Faiss.py
使用spacy和text2vec将文本编码为句向量。定义了Faiss类,封装了一个Faiss索引的构建、添加样本、搜索相似样本、保存等功能。实现语义相似句检索的核心代码,通过词向量技术编码句子语义,以及高效的向量空间索引Faiss实现快速相似度搜索。
- Faiss类
  - add\_doc函数
    将完整文档添加到向量索引和文档库中的过程，同时记录各段落和文档的信息，包括偏移、起止、页码等。
  - search\_doc函数
    优先选择完整文档相似度最大的，并且过滤掉低于阈值的结果。
  - dump函数
    将构建好的Faiss索引保存到文件。

# Usage
预处理文本
```python3
from faisslate.document import formal

print(formal("要整理的文本字符串"))
```
将预处理好的文本，添加到向量数据库中
```python3
from faisslate.document import split
from faisslate.Faiss import Faiss

source = "预处理好的文本的唯一ID"
paras = split("预处理好的文本字符串")

Faiss.save_dir = "向量数据库存放目录"
db = Faiss("向量数据库名字")
db.add_doc(source, {'paras': paras})
db.dump()
```
查询，然后显示匹配的文本段落
```python3
from faisslate.Faiss import Faiss

Faiss.save_dir = "向量数据库存放目录"
db = Faiss("向量数据库名字")
results = db.search_doc("与这段文字进行相似匹配")
for result in results:
    source = result['source'] # 预处理好的文本的唯一ID
    score  = result['score']  # 相似度
    pages  = result['pages']  # 匹配的段落下标

    print(f"{source}: {score}")
    doc = db.docs[source]
    paras = doc['paras']
    for page in pages:
        para = paras[page]
        print(para['text']+para['sep'])
```

# Contact us
<may.xiaoya.zhang@gmail.com>
