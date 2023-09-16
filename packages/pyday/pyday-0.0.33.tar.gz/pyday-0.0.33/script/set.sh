python3 -m venv .venv
source $(pwd)/.venv/bin/activate
pip install --upgrade pip

# 數據分析
pip install pandas
pip install numpy

pip install opencc
# pip install opencc-python-reimplemented
pip install nltk

# 數據可視化
pip install matplotlib
pip install wordcloud
pip install pyecharts

# 機器學習
pip install scikit-learn
pip install notebook
pip install jupyterlab

# 格式化，導出包
pip install autopep8
pip install flit

# 依賴包
pip freeze > requirements.txt

# touch pyproject.toml

# flit build
# python3 -m twine upload --repository testpypi dist/*

# python3 -m pip install --upgrade build
# python3 -m pip install --upgrade twine

# pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pyday-AnsonCar==0.0.17
# jupyter kernelspec remove kernelname
# touch pyproject.toml
# git clone https://github.com/pyecharts/pyecharts-gallery.git

# python -m ipykernel install --user --name py31010 --display-name "Python (3.10.10)"

# git clone https://github.com/pyecharts/pyecharts-gallery.git

# https://clay-atlas.com/blog/2019/11/25/python-chinese-tutorial-cloudword-demo/?amp=1

# https://clay-atlas.com/blog/2019/09/25/python-chinese-tutorial-tokenizer-thulac/?amp=1

# https://developer.aliyun.com/article/97455

# https://blog.csdn.net/weixin_39920403/article/details/110052433

# if not "ipykernel" in sys.modules:
#     self.loadDir()