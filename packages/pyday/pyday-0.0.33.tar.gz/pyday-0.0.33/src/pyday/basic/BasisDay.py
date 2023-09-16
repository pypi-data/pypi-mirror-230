import os
from . import config

class BasisDay:
    def __init__(self, package):
        self.inPath = os.path.join( config.worKdir, f"pydayData/{package}" )
        self.toPath = os.path.join( config.worKdir, f"pydayDist/{package}" )
    
    # inPath
    def setPath(self, inPath): 
        # if not os.path.exists(inPath):
        #     os.mkdir(inPath)
        self.inPath = inPath
        
    def getPath(self):
        return self.inPath
    
    # toPath
    def setToPath(self, toPath):
        # if not os.path.exists(toPath):
        #     os.mkdir(toPath)
        self.toPath = toPath

    def getToPath(self):
        return self.toPath

    # 生成文件
    def loadDir(self, pathList):
        # 如果沒有此路徑會自動生成 If the path does not exist, the directory will be created
        for path in pathList:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)