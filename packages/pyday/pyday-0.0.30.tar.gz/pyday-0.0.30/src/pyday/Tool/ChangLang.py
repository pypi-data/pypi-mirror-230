import os
from opencc import OpenCC
from googletrans import Translator

from ..basic import config
from ..basic.BasisDay import BasisDay

# ChangLanguage
class ChangLang(BasisDay):
    # constructor
    def __init__(self, text=None):
        self.data = "null"
        self.tc = "null"
        self.sc = "null"
        self.en = "null"
        
        self.cc = OpenCC()
        self.translator = Translator()
        
        if isinstance(text, str):
            self.setData(text)
        
    # method
    # input
    def inFile(self, file):
        with open(file) as f:
            self.data = f.read()
            self.setData(self.data)
            
    def setData(self, data) -> None:
        self.data = str(data)
        self.reload()
    
    # output
    def toFile(self, fileName, data):
        # 寫入文件
        with open(fileName, "w") as f:
            f.write(data)
            
    # Chang Way
    def tt2tc(self):
        self.cc.set_conversion('s2t')
        return self.cc.convert(self.data) 

    def tc2sc(self):
        self.cc.set_conversion('t2s')  
        return self.cc.convert(self.data)

    def tc2en(self):
        try:
            self.en = self.translator.translate(self.tc, dest='en').text
        except:
            self.en = "null"
        return self.en
    
    def en2tc(self,data):
        try:
            return self.translator.translate(data, dest='zh-TW').text
        except:
            return "null"
        
    def reload(self):
        self.tc = self.tt2tc()
        self.sc = self.tc2sc()
        self.en = self.tc2en()
        
    # Basic 一般
    def __str__(self) -> str:
        return "\n" + self.tc + "\n" + self.sc + "\n" + self.en + "\n"

    def __repr__(self) -> str:
        return "\n" + self.tc + "\n" + self.sc + "\n" + self.en + "\n"
    
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