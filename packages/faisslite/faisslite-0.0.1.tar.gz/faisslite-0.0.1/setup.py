from setuptools import setup, find_packages

# 学习了这篇文章：https://zhuanlan.zhihu.com/p/276461821
# 总结一下就是先写个 setup.py 文件，然后按照下面步骤操作：
# python3 setup.py sdist
# python3 setup.py register
# python3 setup.py sdist upload
setup(
    name='faisslite',
    version='0.0.1',
    author='may.xiaoya.zhang',
    author_email='may.xiaoya.zhang@gmail.com',
    url='https://pypi.org/user/May.xiaoya.zhang/',
    description='Faiss向量数据库建立',
    packages=find_packages(),
    install_requires=['spacy>=3.5.3', 'faiss>=1.7.4', 'numpy>=1.24.3'],
    data_files=[
        ('.', [
            'document.py',
            'Faiss.py'
        ])
    ]
)
