# DataReader 指令大全
## 基本
```python
from pyday import DataReader

# 構建實例
dr = DataReader() 
dr = DaatDeader("test.csv")
```

## 引入
```python
# 引入文件
# 請存放文件在 pydayData/reader 目錄下
# 如果沒有此路徑會自動生成
dr.inFile("test.csv") 
```

## 輸出
```python
# 輸出文件
# 生成文件在 pydayDist/reader 目錄下
# 如果沒有此路徑會自動生成
# 目前只支持csv, json, xlsx
dr.toFile("test2.csv")
dr.toFile("test2.json")
dr.toFile("test2.xlsx")
# 如果 格式為 all，會生成 所有支持的格式
dr.toFile("test2.all") 
```

## 設定路徑
```python
# 查看引入文件目錄
dr.getPath()

# 改變引入文件目錄
dr.setPath(path) 

# 查看輸出文件目錄
dr.getToPath()

# 改變輸出文件目錄
dr.setToPath(path) 
```

## 䌓簡轉換 Words
```python
dr.inFile("xx.docx")
dr.toFile("xx.docx", "sc")

# 可以 轉為 英文（需連網）
dr.toFile("xx.docx", "en")
```
