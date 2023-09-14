# Tool 工具箱 指令大全
## dirTree 文件樹狀結構
<!-- File Tree Structure -->
```python
from pyday import dirTree

# 不顯示的文件
exclude_list = [".DS_Store", ".github", ".venv", ".git", ".gitignore", ".gitattributes", "test", "__pycache__"]

# 生成 Tree
# max_depth 最大深度
dirTree( ".", exclude_list, max_depth=1 )
```
