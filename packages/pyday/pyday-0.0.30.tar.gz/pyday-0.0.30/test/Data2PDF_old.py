import sys
sys.path.append('..')
import os
import json
from ..basic import config
from ..ChangLanguage import *
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    PageBreak,
    Image,
    TableStyle,
    Table,
)
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black

# 字體
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 寫入字體
for name, path in config.font_ttf.items():
    pdfmetrics.registerFont(TTFont(name, path))

styles = getSampleStyleSheet()
# 標題
Tile_TC = ParagraphStyle(
    "styleNormalCustom",
    fontName="Noto_Sans_TC_Bold",
    parent=styles["Normal"],
    alignment=TA_CENTER,
    fontSize=18,
    leading=24,
    # textColor=HexColor("#4f71bd")
)
# 副標題
SubTile_TC = ParagraphStyle(
    "styleNormalCustom",
    fontName="Noto_Sans_TC_Bold",
    parent=styles["Normal"],
    alignment=TA_LEFT,
    fontSize=16,
    leading=22,
)
# 副標題2
SubTile2_TC = ParagraphStyle(
    "styleNormalCustom",
    fontName="Noto_Sans_TC_Bold",
    parent=styles["Normal"],
    alignment=TA_LEFT,
    fontSize=16,
    leading=22,
    leftIndent=16 * 2,
)
# 內文（一般/基礎)
Basis_TC = ParagraphStyle(
    "styleNormalCustom",
    fontName="Noto_Sans_TC_Regular",
    parent=styles["Normal"],
    alignment=TA_LEFT,
    fontSize=12,
    leading=20,
)
# 內文2（一般/基礎)
Basis2_TC = ParagraphStyle(
    "styleNormalCustom",
    fontName="Noto_Sans_TC_Regular",
    parent=styles["Normal"],
    alignment=TA_LEFT,
    fontSize=12,
    leading=20,
    leftIndent=16 * 2,
)

Tile_SC = ParagraphStyle(
    "styleNormalCustom",
    fontName="Noto_Sans_SC_Bold",
    parent=styles["Normal"],
    alignment=TA_CENTER,
    fontSize=18,
    leading=24,
    # textColor=HexColor("#4f71bd")
)
# 副標題
SubTile_SC = ParagraphStyle(
    "styleNormalCustom",
    fontName="Noto_Sans_SC_Bold",
    parent=styles["Normal"],
    alignment=TA_LEFT,
    fontSize=16,
    leading=22,
)
# 副標題2
SubTile2_SC = ParagraphStyle(
    "styleNormalCustom",
    fontName="Noto_Sans_SC_Bold",
    parent=styles["Normal"],
    alignment=TA_LEFT,
    fontSize=16,
    leading=22,
    leftIndent=16 * 2,
)
# 內文（一般/基礎)
Basis_SC = ParagraphStyle(
    "styleNormalCustom",
    fontName="Noto_Sans_SC_Regular",
    parent=styles["Normal"],
    alignment=TA_LEFT,
    fontSize=12,
    leading=20,
)

# 內文2（一般/基礎)
Basis2_SC = ParagraphStyle(
    "styleNormalCustom",
    fontName="Noto_Sans_SC_Regular",
    parent=styles["Normal"],
    alignment=TA_LEFT,
    fontSize=12,
    leading=20,
    leftIndent=16 * 2,
)


class Data2PDF:
    # constructor
    def __init__(self, inFile=""):
        # about inptut file name, check the name and extension (文件後綴)
        self.fileName = inFile
        self.fileFormat = inFile.split(".")[-1]
        # set the read data path
        self.setPath(config.worKdir + "/data")
        self.setImgPath(config.worKdir + "/data/img/")
        self.data = self.inFile(inFile) if inFile != "" else []

    # Setter
    def inFile(self, inFile):
        self.fileName = inFile
        self.fileFormat = inFile.split(".")[-1]
        file = os.path.join(self.path, inFile)
        with open(file, "r") as fileJson:
            self.data = json.loads(fileJson.read())["data"]
        return self.data

    def inText(self, data, cl="tc"):
        Text = {
            "Title": Tile_TC if cl == "tc" or "tt" else Tile_SC,
            "SubTitle": SubTile_TC if cl == "tc" or "tt" else SubTile_SC,
            "SubTitle2": SubTile_TC if cl == "tc" or "tt" else SubTile2_SC,
            "SubTitle2": SubTile_TC if cl == "tc" or "tt" else SubTile2_SC,
            "Basis": Basis_TC if cl == "tc" or "tt" else Basis_SC,
            "Basis2": Basis2_TC if cl == "tc" or "tt" else Basis2_SC,
        }
        if data[0].lower() == "title":
            return Paragraph(data[1], Text["Title"])
        elif data[0].lower() == "subtitle":
            return Paragraph(data[1], Text["SubTitle"])
        elif data[0].lower() == "subtitle2":
            return Paragraph(data[1], Text["SubTitle2"])
        elif data[0].lower() == "text":
            return Paragraph(data[1], Text["Basis"])
        elif data[0].lower() == "text2":
            return Paragraph(data[1], Text["Basis2"])

    def inImg(self, img):
        img = os.path.join(self.ImgPath, img)
        img_reader = ImageReader(img)
        img_width, img_height = img_reader.getSize()
        max_width, max_height = self.pdf.width, self.pdf.height
        if img_width > max_width or img_height > max_height:
            ratio = min(max_width / img_width, max_height / img_height)
            img_width *= ratio
            img_height *= ratio
        return Image(
            img,
            width=img_width,
            height=img_height
        )

    def inTable(self, data):
        tableStyle = TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # 置中對齊
                ("FONTNAME", (0, 0), (-1, -1), "Noto_Sans_TC_Regular"),  # 字體
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # 上下置中
                ("GRID", (0, 0), (-1, -1), 0.5, black),  # 框線黑色，寬度0.5
            ]
        )
        return Table(
            data[1],
            style=tableStyle,
            colWidths=self.pdf.width / len(data[1][0]),
            spaceBefore=12,
            spaceAfter=12,
        )

    def setPath(self, path):
        self.path = path

    def setImgPath(self, path):
        self.ImgPath = path

    # 寫入頁碼
    def infooter(self, canvas, doc):
        # 在 PDF 頁面底部寫入頁碼
        canvas.saveState()
        canvas.drawString(doc.width + doc.rightMargin, 20, f"{doc.page}")
        canvas.restoreState()

    def getPath(self):
        path = f"Data Path: {self.path}"
        return path
    def getImgPAth(self):
        ImgPath = f"Img Path: {self.ImgPath}"
        return ImgPath

    # getter
    def toFile(self, toFile, footer=True, cl="tt"):
        self.pdf = SimpleDocTemplate(
            f"{config.worKdir}/dist/{toFile}",
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )
        # get the file data
        data = []
        for line in self.data:
            if line[0] == "img":
                set = self.inImg(line[1])
            elif line[0].lower() == "table":
                set = self.inTable(line)
            else:
                if cl == "tc":
                    cc = ChangLang()
                    cc.setData(line[1])
                    line[1] = cc.tc
                elif cl == "sc":
                    cc = ChangLang()
                    cc.setData(line[1])
                    line[1] = cc.sc
                elif cl == "en":
                    cc = ChangLang()
                    cc.setData(line[1])
                    line[1] = cc.en
                set = self.inText(line, cl)
            data.append(set)
        # 將數據轉換為 PDF 文件。
        if footer:
            # 如果需要在 PDF 頁面底部添加頁碼，則設置 onFirstPage 和 onLaterPages 參數，並生成 PDF 文件。
            self.pdf.build(data, onFirstPage=self.infooter, onLaterPages=self.infooter)
        else:
            # 如果不需要在 PDF 頁面底部添加頁碼，則直接生成 PDF 文件。
            self.pdf.build(self.data)


# https://ithelp.ithome.com.tw/articles/10239020
# https://docs.reportlab.com/reportlab/userguide/ch7_tables/

# 這是 ReportLab 中 Table 類別的建構式（constructor）的參數說明：

# data：必要參數，要顯示在表格中的資料，格式為二維的列表或元組。
# colWidths：一個列表，包含每個欄位的寬度（以 point 為單位，1 inch = 72 points）。如果沒有指定，則根據內容自動調整欄位寬度。
# rowHeights：一個列表，包含每個列的高度（以 point 為單位）。如果沒有指定，則根據內容自動調整列高度。
# style：一個 TableStyle 物件，包含表格的樣式設置（如文字對齊、框線顏色等）。
# splitByRow：一個布林值或整數。如果是 True 或 1，表示當表格太長無法顯示在當前頁面時，自動將表格拆分成多個子表格，並顯示在多個頁面上。如果是 False 或 0，表示整個表格只顯示在一頁中，而超出頁面的部分會被切割掉。也可以指定要拆分的行數。
# repeatRows：一個整數，表示在每個新頁面上是否要重複顯示表格的前幾行。預設值為 0，表示不重複顯示。
# repeatCols：一個整數，表示在每個新頁面上是否要重複顯示表格的前幾列。預設值為 0，表示不重複顯示。
# rowSplitRange：一個元組，表示每個子表格中要顯示的行數範圍。例如，如果 rowSplitRange=(0, 2)，表示每個子表格只顯示前 2 行。
# spaceBefore：一個浮點數，表示表格上方的空白間距（以 point 為單位）。
# spaceAfter：一個浮點數，表示表格下方的空白間距（以 point 為單位）。
# cornerRadii：一個元組，表示表格的四個角的半徑（以 point 為單位，順序為左上、右上、右下、左下）。預設值為 None，表示不設置圓角。
