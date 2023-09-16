# PyDay 快速開始
## 什麼是 PyDay？
PyDay 的宗旨，是提供統一接口和功能集及一些有用的功能，使代碼更簡潔和易於維護，例如䌓簡英轉換、解壓縮（想當年泰迪杯...）等。  

## 快速開始
### PyPi 安裝
```shell
pip install pyday
```

### 示例
#### 使用 DataReader
```python
from pyday import DataReader
dr = DataReader("test.csv")
dr.toFile("test2.xlsx")
```

#### DataVis
```python
from pyday import DataVis

```

#### 使用 Data2PDF 
```python
from pyday import Data2PDF
import pyday
d2pdf = Data2PDF("test.json")
d2pdf.toFile("mypdf.pdf")
```