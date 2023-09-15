# faisslite about
一个用于中文文本向量化和相似度搜索的Python包。它可以将中文段落表征为向量矩阵,并构建向量搜索索引,用于快速准确检索文本中的相似句子。

## document.py
对输入文本进行规范化处理，并将输入文本拆分成段落。
- formal函数
  实现文本的预处理功能，输入原始文本,可以输出规范化了格式的文本内容。
- split函数
  将文本拆分为由文本段落和分隔符构成的字典，为后续向量化处理文本提供了基础。

## Faiss.py
使用spacy和text2vec将文本编码为句向量。定义了Faiss类,封装了一个Faiss索引的构建、添加样本、搜索相似样本、保存等功能。实现语义相似句检>索的核心代码,通过词向量技术编码句子语义,以及高效的向量空间索引Faiss实现快速相似度搜索。
- encode函数
  采用text2vec-base-chinese生成Vector向量，采用spacy的中文模型生成Vector2向量，两个向量加权得到最终向量。
- top1函数
  找出选出结果的最大值
- Faiss类
  - add函数
    将段落拆解成句子，逐句向量化之后构建索引或者添加向量。
  - add\_doc函数
    将完整文档添加到向量索引和文档库中的过程，同时记录各段落和文档的信息，包括偏移、起止、页码等。
  - search函数
    优先选择相似度最大，并且过滤掉低于阈值的结果。合并Faiss搜索出来的多个向量结果，得到按相似度排序的top-k个文本匹配。
  - dump函数
    将构建好的Faiss索引保存到文件。

# Director 

+ faisslite 
    + \_\_init\_\_.py
    + document.py
    + Faiss.py
+ setup.py
+ README.md

# Install
`$ pip3 install -U faisslite`

# Usage
`$ python3 -m faisslite &`

# Contact us
<may.xiaoya.zhang@gmail.com>
