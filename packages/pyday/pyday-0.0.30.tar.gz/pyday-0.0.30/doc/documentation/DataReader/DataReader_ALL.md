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
dr.inFile("test.csv")

# 查看引入文件目錄
dr.getPath()

# 改變引入文件目錄
dr.setPath(path)  # 如果沒有此路徑會自動生成

```

## 輸出
```python
# 目前只支持csv, json, xlsx
dr.toFile("test2.csv")
dr.toFile("test2.json")
dr.toFile("test2.xlsx")
# 如果 格式為 all，會生成 所有支持的格式
dr.toFile("test2.all")

# 查看輸出文件目錄
dr.getToPath()

# 改變輸出文件目錄
dr.setToPath(path)  # 如果沒有此路徑會自動生成
```

## 檢查文件夾是否存在及生成
```python
# 初始化時會使用，如果為jupyter環境不會執行此方法。
dr.loadDir()  # 如果沒有此路徑會自動生成
```

