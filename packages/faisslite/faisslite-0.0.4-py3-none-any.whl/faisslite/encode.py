# pip3 install spacy
# python3 -m spacy download zh_core_web_sm
# https://spacy.io/usage
# https://spacy.io/api/span
import spacy
# https://pypi.org/project/text2vec/
from text2vec import SentenceModel
# https://blog.csdn.net/hqh131360239/article/details/79061535
import numpy

spacy_gpu = spacy.prefer_gpu()
print("spacy_gpu?", spacy_gpu)
nlp = spacy.load('zh_core_web_lg')

model = SentenceModel('shibing624/text2vec-base-chinese')

def encode(para):
    doc = nlp(para)
    Vector = []
    Text = []
    for sent in filter(lambda x:x.has_vector, doc.sents):
        Vector.append((sent.vector/sent.vector_norm).tolist())
        Text.append(sent.text)
    Vector = numpy.array(Vector)

    Vector2 = model.encode(Text)
    # faiss.normalize_L2(Vector2)用下面两行代码实现。
    Vector2_norm = numpy.linalg.norm(Vector2, axis=1, keepdims=True)
    Vector2 = Vector2/Vector2_norm

    """
    已知：|V2| = 1，|V| = 1
    问题：|(a×V2,b×V)| = 1
    推导：|(a×V2,b×V)|
        = sqrt((a×V2,b×V)⋅(a×V2,b×V))
        = sqrt(|a×V2|^2+|b×V|^2)
        = sqrt(a^2+b^2)
    结论：{(a,b)|a^2+b^2=1}
    例如：{(0.7071,0.7071), (0.8,0.6), ...}
    """
    Vector = numpy.hstack((Vector2 * 0.8, Vector * 0.6))
    return(Vector, Text)
