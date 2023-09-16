<p align="center">
    <img width="192px" src="./doc/Logo/AnsonLogo01.png" >
</p>
<h1 align="center"><b>PyDay</b></h1>

<p align="center">Python 工具一條龍</p>
<p align="center">v0.0.33</p>

---

## 宗旨
PyDay 的宗旨，是提供統一接口和功能集，使代碼更簡潔和易於維護。  
<!-- PyDay 是一個綜合工具包，主要用於數據分析和數據可視化，封裝了pandas, numpy, matplotlib等常用包。   -->
<!-- 除了數據分析和數據可視化之外， -->
Pyday 提供了一些有用的功能，例如䌓簡英轉換、解壓縮（想當年泰迪杯...）等。  

---

## 簡介
### 框架由以下基本模組構成：
1. DataReader (開發中)
2. DataVis (未開發)
3. Data2PDF 用於生成PDF (開發中)
4. Tool 
   1. ChageLang 用於翻譯 (完工)
   2. dirTree 生成文件樹 (完工)
   3. unzip 解壓縮 (開發中)
<!-- Machine Learning 機器學習 -->

### 優勢
有時庫可能會不支持顯示中文字體，需要自已再設定字體。  
而本項目使用了google開源字體 Noto Sans，全面支持中文字體。

---

## 項目結構
```
*
├── LICENSE 開源證明
├── requirements.txt
├── test 
├── script 有用腳本
├── README.md
├── setup.py 打包庫
├── .gitignore
├── .gitattributes
├── doc 
├── setup.cfg
└── src
    └── pyday
```

---

## 使用方法
### 安裝
```python 
pip install pyday
```

### 測試
```python
import pyday
print(pyday.__version__)
```

---

## 線上資源
**查看 [pypi/pyday主頁](https://pypi.org/project/pyday/)**
**查看 [pyday線上文檔](https://ansoncar.github.io/AC-Note/Document/pyday/guide_tc.html)**

---

## 查閱更多
**查看 [Change Log(更新日志)](https://github.com/AnsonCar/pyday/blob/main/doc/CHANGLOG.md)**
