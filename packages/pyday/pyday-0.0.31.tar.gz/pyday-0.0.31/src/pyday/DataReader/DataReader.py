import os
import sys
import pandas as pd

from docx import Document

from ..basic import config
from ..basic.BasisDay import BasisDay
from ..Tool.ChangLang import ChangLang

class DataReader(BasisDay):
    def __init__(self, inFile=None):
        super().__init__("reader")
        self.fileName = inFile
        self.df = None
        
        if isinstance(inFile, str):
            self.inFile(inFile)
        else:
            self.df = pd.DataFrame(inFile)
    
    def inFile(self, inFile):
        self.loadDir( [self.inPath] )
        inFileFormat = os.path.splitext(inFile)[-1][1:].lower()
        inFile = os.path.join(self.inPath, inFile)
        if os.path.exists(inFile):
            if inFileFormat == "csv":
                self.df = pd.read_csv(inFile)
            elif inFileFormat == "json":
                self.df = pd.read_json(inFile)
            elif inFileFormat == "xlsx":
                self.df = pd.read_excel(inFile)
            elif inFileFormat == "docx":
                self.df = Document(inFile)
            else:
                print( f"input: Does not support '{inFileFormat}' format" )
        else:
            print( f"Did Not Have File: {inFile}" )

    def toFile(self, toFile, isCl="tt"):
        self.loadDir( [self.toPath] )
        toFileFormat = os.path.splitext(toFile)[-1][1:].lower()
        toFile = os.path.splitext(toFile)[0]
        out = f"{self.toPath}/{toFile}"
        if toFileFormat == "docx": 
            # 感謝 https://blog.csdn.net/zwy_0309/article/details/124182699
            doc = self.df
            children = doc.element.body.iter()
            if isCl == "tt":
                self.df.save(f"{out}.docx")
            else:
                for child in children:
                    if child.tag.endswith('txbx'):
                        for ci in child.iter():
                            if ci.tag.endswith('main}t'):
                                if isCl == "sc":
                                    ci.text = ChangLang(ci.text).sc
                                elif isCl == "en":
                                    ci.text = ChangLang(ci.text).en
                                    
                for text in doc.paragraphs:
                    if len(text.text) > 1:
                        if isCl == "sc":
                            text.text = ChangLang(text.text).sc
                        elif isCl == "en":
                            text.text = ChangLang(text.text).en
                if isCl == "sc":
                    self.df.save(f"{ChangLang(out).sc}.docx")
                elif isCl == "en":
                    self.df.save(f"{ChangLang(out).en}.docx")
        else:
            if toFileFormat == "all":
                self.df.to_csv( f"{out}.csv", index=False)
                self.df.to_json( f"{out}.json")
                self.df.to_excel( f"{out}.xlsx" )
            elif toFileFormat == "csv":
                self.df.to_csv( f"{out}.csv", index=False)
            elif toFileFormat == "json":
                self.df.to_json( f"{out}.json")
            elif toFileFormat == "xlsx":
                self.df.to_excel( f"{out}.xlsx", index=False)
            else:
                print( "output: Does not support" )
