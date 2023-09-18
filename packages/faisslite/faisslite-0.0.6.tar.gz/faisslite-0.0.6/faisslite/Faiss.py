from faisslite.encode import encode
# https://zhuanlan.zhihu.com/p/107241260
# https://zhuanlan.zhihu.com/p/350957155
# https://ispacesoft.com/85864.html
# https://zhuanlan.zhihu.com/p/530958094
import faiss
import os, json

faiss_gpu = faiss.get_num_gpus()
print("faiss_gpu=", faiss_gpu)

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

    def search(self, para, top_k=100, threshold=0.6):
        Vector, Text = encode(para)
        if not Vector.shape[0]: return []

        Score, Index = self.faiss_index.search(Vector, top_k)
        Result = []
        for i in range(Index.shape[0]):
            result = []
            for j in range(Index.shape[1]):
                if Index[i, j] < 0 or Score[i, j] < threshold: break
                result.append((Score[i, j], Index[i, j]))
            Result.append(result)
        return Result

    def search_doc(self, para, near=0.001, **kwargs):
        Result = self.search(para, **kwargs)
        Docs = {}
        for result in Result:
            docs = {}
            for score, index in result:
                p = self.paras[index]
                source = p['source']
                if source not in docs:
                    docs[source] = {
                        'score': score,
                        'pages': set()
                    }
                docs[source]['pages'].add(p['page'])
            for source in docs:
                if source not in Docs:
                    Docs[source] = {
                        'score': 0.0,
                        'pages': set()
                    }
                Docs[source]['score'] += docs[source]['score']
                Docs[source]['pages'] |= docs[source]['pages']

        Result = [
            {
                'source': source,
                'score': Docs[source]['score'],
                'pages': sorted(list(Docs[source]['pages']))
            }
            for source in Docs
        ]
        Result = sorted(Result, key=lambda item:item['score'], reverse=True)
        return filter(lambda x:Result[0]['score']-x['score'] < near, Result)

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
