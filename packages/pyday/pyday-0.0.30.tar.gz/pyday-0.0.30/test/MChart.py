import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontManager
import matplotlib.font_manager as fm
from abc import ABC, abstractmethod

# import opencc
# converter = opencc.OpenCC('s2t.json')
# converter.convert('汉字')  # 漢字

class MCharts(ABC):
    def __init__(self):
        self.width = 800
        self.height = 600
        matplotlib.rc("font", family='Heiti TC')

    def font(self):
        mpl_fonts = set(f.name for f in FontManager().ttflist)
        print('all font list get from matplotlib.font_manager:')
        for f in sorted(mpl_fonts):
            print('\t' + f)

    def set_font(self, font):
        matplotlib.rc("font", family=font)

    def set_size(self):
        plt.figure(figsize=(self.width/100, self.height/100))

    @abstractmethod
    def in_file(self):
        pass

    @abstractmethod
    def in_data(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def to_file(self):
        pass
