from faisslite.encode import encode
# https://zhuanlan.zhihu.com/p/107241260
# https://zhuanlan.zhihu.com/p/350957155
# https://ispacesoft.com/85864.html
# https://zhuanlan.zhihu.com/p/530958094
import faiss
import os, json

faiss_gpu = faiss.get_num_gpus()
print("faiss_gpu=", faiss_gpu)

def top_1(Score, pos):
    i = 0
    for j in range(1, len(pos)):
        if Score[i, pos[i]] < Score[j, pos[j]]: i = j
    return i

class Faiss:
    save_dir = '.'
    def __init__(self, name):
        self.faiss_path = f'{Faiss.save_dir}/{name}.index'
        if not os.path.exists(self.faiss_path):
            self.faiss_index = None
            self.sents = []
            self.paras = []
            self.docs = {}
        else:
            self.load()

    def cpu_to_gpu(self):
        res = faiss.StandardGpuResources()
        self.faiss_index = faiss.index_cpu_to_gpu(res, 0, self.faiss_index)

    def gpu_to_cpu(self):
        self.faiss_index = faiss.index_gpu_to_cpu(self.faiss_index)

    def add(self, para):
        Vector, Text = encode(para)
        if not Vector.shape[0]: return
        if not self.faiss_index:
            # L2 欧几里得距离（空间距离）
            # IP 内积算法（Inner Product）
            self.faiss_index = faiss.IndexFlatIP(Vector.shape[1])
            if faiss_gpu > 0: self.cpu_to_gpu()
        self.faiss_index.add(Vector)
        self.sents.extend(Text)
        assert self.faiss_index.ntotal == len(self.sents)

    def add_doc(self, source, doc):
        if source in self.docs: return
        doc['start'] = len(self.paras)
        page = 0
        for para in doc['paras']:
            start = len(self.sents)
            self.add(para['text'])
            end = len(self.sents)
            assert start < end
            self.paras.extend([{
                'source': source,
                'page': page,
                'start': start,
                'end': end
            }] * (end-start))
            page += 1
        assert len(self.sents) == len(self.paras)
        doc['end'] = len(self.paras)
        self.docs[source] = doc

    def search(self, para, top_k=100, threshold=0.67):
        Vector, Text = encode(para)
        Score, Index = self.faiss_index.search(Vector, top_k)

        # 对选出的结果合并排序
        score, index = [], []
        pos = [0] * Index.shape[0]
        while True:
            i = top_1(Score, pos)
            if Index[i, pos[i]] < 0 or Score[i, pos[i]] < threshold: break
            index.append(Index[i, pos[i]])
            score.append(Score[i, pos[i]])
            pos[i] += 1
            if pos[i] >= top_k: break
        return(score, index)

    def search_doc(self, para, **kwargs):
        score, index = self.search(para, **kwargs)
        docs = {}
        for i in range(len(index)):
            p = self.paras[index[i]]
            source = p['source']
            if source not in docs:
                docs[source] = {
                    'score': 0.0,
                    'pages': set()
                }
            docs[source]['score'] += score[i]
            docs[source]['pages'].add(p['page'])
        docs = [
            {
                'source': k,
                'score': v['score'],
                'pages': sorted(list(v['pages']))
            }
            for k,v in docs.items()
        ]
        return sorted(docs, key=lambda item:item['score'], reverse=True)

    def load(self):
        self.faiss_index = faiss.read_index(self.faiss_path+'/index.faiss')
        if faiss_gpu > 0: self.cpu_to_gpu()
        with open(self.faiss_path+'/index.sents', 'r', encoding='utf-8') as f:
            self.sents = json.load(f)
        with open(self.faiss_path+'/index.paras', 'r', encoding='utf-8') as f:
            self.paras = json.load(f)
        with open(self.faiss_path+'/index.docs', 'r', encoding='utf-8') as f:
            self.docs = json.load(f)

    def dump(self):
        if not os.path.exists(self.faiss_path): os.mkdir(self.faiss_path)
        if faiss_gpu > 0: self.gpu_to_cpu()
        faiss.write_index(self.faiss_index, self.faiss_path+'/index.faiss')
        if faiss_gpu > 0: self.cpu_to_gpu()
        with open(self.faiss_path+'/index.sents', 'w', encoding='utf-8') as f:
            json.dump(self.sents, f, ensure_ascii=False, indent=2)
        with open(self.faiss_path+'/index.paras', 'w', encoding='utf-8') as f:
            json.dump(self.paras, f, ensure_ascii=False, indent=2)
        with open(self.faiss_path+'/index.docs', 'w', encoding='utf-8') as f:
            json.dump(self.docs, f, ensure_ascii=False, indent=2)
