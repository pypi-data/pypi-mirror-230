from setuptools import setup, find_packages
from pathlib import Path

# 将当前目录README读取为long_description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# 学习了这篇文章：https://zhuanlan.zhihu.com/p/276461821
# 总结一下就是先写个 setup.py 文件，然后按照下面步骤操作：
# python3 setup.py sdist
# python3 setup.py register
# python3 setup.py sdist upload
setup(
    name='faisslite',
    version='0.0.4',
    author='may.xiaoya.zhang',
    author_email='may.xiaoya.zhang@gmail.com',
    url='https://pypi.org/user/May.xiaoya.zhang/',
    description='创建/查询Faiss向量数据库',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown'
)
