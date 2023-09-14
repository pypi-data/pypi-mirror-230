import os
import sys

def dirTree(path, exclude_list=None, level=0, maxLevel=None, firstLast=False):
    # 取得當前目錄所有文件
    files = os.listdir(path)
    # 遍历列表
    for num, file in enumerate(files):
        # 如果不要顯示的文件就跳
        if (exclude_list is not None) and file in exclude_list:
            continue

        # 判斷是否為最後一項
        isLast = len(files) - 1 == num
        prefix = "└── " if isLast else "├── "
        if level == 0:
            print( prefix + file )
        else:
            if firstLast:
                print( "    " + "│   "*(level-1) + prefix + file )
            else:
                print( "│   " * level + prefix + file )
    
        isDir = os.path.isdir(os.path.join(path, file))
        
        if not firstLast:
            firstLast = level == 0 and isLast
        if isDir and (maxLevel is None or level < maxLevel):
            dirPath = os.path.join(path, file)
            dirTree(dirPath, exclude_list,level=level+1, maxLevel=maxLevel, firstLast=firstLast)
