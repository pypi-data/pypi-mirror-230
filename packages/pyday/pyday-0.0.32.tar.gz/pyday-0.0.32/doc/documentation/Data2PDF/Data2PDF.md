# Data2PDF
Data2PDF 是基於 reportlab 開發的，用於生成PDF。

## 建構實例 - 初始化
接受兩種初始化方法：
**第一種，不帶參數。使用inFile()引入需要讀取的文件。**
```python
from pyday import Data2PDF
d2pdf = Data2PDF()
d2pdf.inFile("test.json")
```
**第二種，帶有參數。初始化同時引入需要讀取的文件。**
```python
from pyday import Data2PDF
d2pdf = Data2PDF("test.json")
```

---

## 引入資料
引入生成PDF的資料文件，只接受 str (json文件名稱) 和 dict 兩種 datatype
不可以寫路徑連文件名稱，Data2PDF會
### 引入方法
```python
d2pdf.inFile("文件名")
```

### 默認 inFile 路徑
默認inFile路徑為```/data```和```/data/img```，Data2PDF會從這𥚃拿取目標文件和相片。

#### 查看路徑：
```python
print( d2pdf.getPath() ) # 文件路徑
print( d2pdf.getImgPath() ) # 相片路徑
```
#### 改變路徑：
```python
d2pdf.setPath("文件路徑")
d2pdf.setImgPath("相片路徑")
```

### 文件格式
```json
{
    "data": [
        [ "Title", "測試生成PDF" ],
        [ "SubTitle", "這是副標題"],
        [ "text", "這個是PDF生成的內容" ],
        [ "img", "test.png" ],
        [ "Table",
            [
                ["1", "2", "3", "4"],
                ["5", "6", "7", "8"],
                ["9", "10", "11", "12"],
                ["13", "14", "15", "16"]
            ]
        ]
    ]
}
```

第一個元素用來定義樣式，第二個元素用來定義內容
```python
[ "樣式", 內容 ]
```

---

## 生成 PDF
### 生成方法
```python
d2pdf.toFile("myPDF.pdf")
```
### 頁碼
默認生成頁碼 ```footer=True```
```python
d2pdf.toFile( "myPDF.pdf", footer=False ) # 關閉頁碼功能
```

### 翻譯資料
默認不會翻譯文件，如果有需要可以將文件資料所有中文字統一為䌓體，或者簡體，亦可以翻譯為英文。
```python
d2pdf.toFile("myPDF_tc.pdf", cl="tc") # 䌓體中文
d2pdf.toFile("myPDF_sc.pdf", cl="sc") # 簡體中文
d2pdf.toFile("myPDF_en.pdf", cl="en") # 英文
```
> 翻譯功能 基於 googletrans 開發，如果不能上網，文字會變成 null
<!-- > 未來會新增 英文 翻譯 中文 -->

### 默認 toFile 路徑
默認inFile路徑為```/pydayDist```，Data2PDF生成的PDF會存放在這𥚃，如果找不到此文件夾則會自動生成。
#### 查看路徑：
```python
print( d2pdf.getToPath() )
```
#### 改變路徑：
```python
print( d2pdf.setToPath() )
```

---

### 設定樣式
```python

```