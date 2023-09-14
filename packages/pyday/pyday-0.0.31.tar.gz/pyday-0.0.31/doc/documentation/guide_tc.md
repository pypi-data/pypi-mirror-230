# PyDay 指南
## 什麼是 PyDay？
PyDay 的宗旨，是提供統一接口和功能集，使代碼更簡潔和易於維護。

PyDay 是一個綜合工具包，主要用於數據分析和數據可視化，封裝了pandas, numpy, matplotlib等常用包。

除了數據分析和數據可視化之外，Pyday 還提供了一些有用的功能，例如䌓簡英轉換、生成PDF等。 

## 快速開始
### PyPi 安裝
```shell
pip install pyday
```
> 目前未上載到PyPi，，請自行下載gitHub文件

### 示例
#### 使用 DataReader
```python
from pyday import DataReader
import pyday
dr = DataReader("test.csv")
dr.toFile("test2.xlsx")
```

#### DataVis
```python
```

#### 使用 Data2PDF 
```python
from pyday import Data2PDF
import pyday
d2pdf = Data2PDF("test.json")
d2pdf.toFile("mypdf.pdf")
```

## 詳細文檔
### [Data2PDF](./Data2PDF.md)
### [DataReader](./dr.md)