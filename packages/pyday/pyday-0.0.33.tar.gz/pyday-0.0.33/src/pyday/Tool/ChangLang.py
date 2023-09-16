import os
from opencc import OpenCC
from googletrans import Translator

from ..basic import config
from ..basic.BasisDay import BasisDay

# ChangLanguage
# class ChangLang(BasisDay):
class ChangLang:
    # constructor
    def __init__(self, text=None):
        # super().__init__("reader")
        self.inData = "null"
        self.tc = "null"
        self.sc = "null"
        
        self.cc = OpenCC()
        self.translator = Translator()
        
        if isinstance(text, str):
            self.setData(text)
        
    # method
    # input
    # def inFile(self, file):
    #     with open(file) as f:
    #         self. k = f.read()
    #         self.inData(self.data)
            
    def setData(self, data) -> None:
        self.inData = str(data)
        self.loadData()
    
    # output
    # def toFile(self, fileName, data):
    #     # 寫入文件
    #     with open(fileName, "w") as f:
    #         f.write(data)

    def loadData(self) -> None:
        self.tc = self.tt2tc()
        self.sc = self.tc2sc()

    # 基本轉換
    def tt2tc(self):
        self.cc.set_conversion('s2t')
        return self.cc.convert(self.inData) 

    def tc2sc(self):
        self.cc.set_conversion('t2s')  
        return self.cc.convert(self.inData)

    # 翻譯功能
    def tc2en(self, data):
        try:
            self.en = self.translator.translate(data, dest='en').text
        except:
            self.en = "null"
        return self.en
    
    def en2tc(self,data):
        try:
            return self.translator.translate(data, dest='zh-TW').text
        except:
            return "null"
    
    # Basic 一般
    def __str__(self) -> str:
        return f"\n{self.tc}\n\n{self.sc}\n"

    def __repr__(self) -> str:
        return f"\n{self.tc}\n\n{self.sc}\n"
    
# opencc 選擇
# hk2s: Traditional Chinese (Hong Kong standard) to Simplified Chinese
# s2hk: Simplified Chinese to Traditional Chinese (Hong Kong standard)
# s2t: Simplified Chinese to Traditional Chinese
# s2tw: Simplified Chinese to Traditional Chinese (Taiwan standard)
# s2twp: Simplified Chinese to Traditional Chinese (Taiwan standard, with phrases)
# t2hk: Traditional Chinese to Traditional Chinese (Hong Kong standard)
# t2s: Traditional Chinese to Simplified Chinese
# t2tw: Traditional Chinese to Traditional Chinese (Taiwan standard)
# tw2s: Traditional Chinese (Taiwan standard) to Simplified Chinese
# tw2sp: Traditional Chinese (Taiwan standard) to Simplified Chinese (with phrases)