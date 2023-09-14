# Data2PDF 指令大全
## 基本
```python
from pyday import Data2PDF

# 構建實例
d2pdf = Data2PDF()
d2pdf = Data2PDF("test.json")
```

## 引入
```python
# 引入文件
d2pdf.inFile("test.json")

# 查看引入文件目錄
d2pdf.getPath()
d2pdf.getImgPath()

# 改變引入文件目錄
d2pdf.setPath(path)  # 如果沒有此路徑會自動生成
d2pdf.setImgPath(path)  # 如果沒有此路徑會自動生成

```

##  輸出
```python
# 輸出PDF文件
d2pdf.toFile("test.pdf")
d2pdf.toFile("test.pdf", footer=True, cl=None)

# 查看輸出文件目錄
d2pdf.getToPath()

# 改變輸出文件目錄
d2pdf.setToPath(path)  # 如果沒有此路徑會自動生成
```

## 檢查文件夾是否存在及生成
```python
# 初始化時會使用，如果為jupyter環境不會執行此方法。
d2pdf.loadDir()  # 如果沒有此路徑會自動生成
```

## 設定樣式
### 字體 Font
```python
d2pdf.addFont(fontName, fontFileName)
```

### 文字 Text
```python
# 內部使用
d2pdf.inText(data, textStyle) 
# 加入字體樣式
# [ [名字], [字體], 對齊方法, 字體大小, 行距, 左縮排, 文字顏色 ]
# TA_LEFT = 0, TA_CENTER = 1, TA_RIGHT = 2, TA_JUSTIFY = 4
textStyle = [ ["Text_TC", "Text_SC"], ["Noto_Sans_TC_Bold", "Noto_Sans_SC_Bold"], 0, 12, 20, 16, 0, "#FFFFFF" ]
d2pdf.addTextStyle(textStyle)
# 查看字體樣式
d2pdf.getTextStyle()
```

### 圖片 Image
```python
# 引入圖片
d2pdf.inImg(imagePath, width=None, height=None)
# 加入圖片樣式
d2pdf.addImg(imageName, imageStyle)
# 查看圖片樣式
d2pdf.getImgStyle()
```

### 表格 Table
```python
# 設定表格
d2pdf.inTable(data, tableStyle)
# 加入表格樣式
d2pdf.setTable(tableStyle)
# 查看表格樣式
d2pdf.getTableStyle()
```

### 頁碼 footer
```python
# 內部使用
d2pdf.infooter()
```