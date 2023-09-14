[1^]:https://md.mzr.me/#:~:text=MdEditor,wn%E6%96%87%E6%A1%A3%E7%9A%84%E7%BC%96%E8%BE%91%E5%99%A8

# About
一个用于中文文本向量化和相似度搜索的Python包。它可以将文本向量化为句向量,并构建向量搜索索引,用于快速检索文本中的相似句子。

>document.py
规范输入文本格式，并将输入文本拆分成段落。实现文本的预处理功能,输入原始文本,可以输出规范化了格式的文本或者进一步拆分为文本段落和分隔符构成的字典,为后续处理文本提供了基础。

>Faiss.py
使用spacy和text2vec将文本编码为句向量,定义了Faiss类,封装了一个Faiss索引的构建、添加样本、搜索相似样本、保存等功能。实现语义相似句检索的核心代码,通过词向量技术编码句子语义,以及高效的向量空间索引Faiss实现快速相似度搜索。
add函数将段落拆解成句子,逐句向量化后加入索引。
add_doc函数将整篇文档中的所有段落加入索引。
search函数给定查询文本,可以搜索文本中最相似的句子。
dump函数可以将构建好的Faiss索引和所有句子样本序列化保存到文件。
支持CPU和GPU两种模式。

# Director 

+ faisslite 
    + \_\_pycache\_\_
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
