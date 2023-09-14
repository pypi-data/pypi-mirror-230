import os
from os import path
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from MChart import MCharts


class WC(MCharts):
    def __init__(self, file: str):
        super().__init__()
        self.__d = path.dirname(
            __file__) if "__file__" in locals() else os.getcwd()
        self.goolge_font = {"SC": "../font/Noto_Sans_SC/NotoSansSC-Regular.otf",
                            "TC": "../font/Noto_Sans_TC/NotoSansTC-Regular.otf"}
        try:
            self.in_file(file)
        except IOError:
            self.in_data(file)

    def in_file(self, file: str):
        text = open(path.join(self.__d, file)).read()
        self.chart = WordCloud(width=800, height=600).generate(text)

    def in_data(self, text: str):
        self.chart = WordCloud(width=800, height=600,
                               font_path=self.goolge_font["SC"]).generate(text)

    def show(self):
        plt.axis("off")
        plt.imshow(self.chart)

    def to_file(self, fileName: str):
        self.chart.to_file(fileName)
        plt.savefig(fileName)
