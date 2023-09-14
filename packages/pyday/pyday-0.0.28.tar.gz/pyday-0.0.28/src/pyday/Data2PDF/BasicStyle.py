import sys
sys.path.append('..')
from ..basic import config
from reportlab.lib.colors import HexColor

# 引入字體 
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 寫入字體
for name, path in config.font_ttf.items():
    pdfmetrics.registerFont(TTFont(name, path))

Text = [
        [ [ "Title_TC", "Title_SC" ], [ "Noto_Sans_TC_Bold", "Noto_Sans_SC_Bold" ] , 1, 18, 24 ],
        [ [ "SubTitle_TC", "SubTitle_SC" ], [ "Noto_Sans_TC_Bold", "Noto_Sans_SC_Bold" ] , 0, 16, 22 ],
        [ [ "SubTilte2_TC", "SubTilte2_SC" ], [ "Noto_Sans_TC_Bold", "Noto_Sans_SC_Bold"], 0, 16, 22, 16*2 ],
        [ [ "Content_TC", "Content_SC" ], [ "Noto_Sans_TC_Regular", "Noto_Sans_SC_Regular"], 0, 12, 20 ],
        [ [ "Content2_TC", "Content2_SC" ], [ "Noto_Sans_TC_Regular", "Noto_Sans_SC_Regular"], 0, 12, 20, 16*2 ],
    ]

# [ ["Content2_TC"], ["Noto_Sans_TC_Bold"], "TA_LEFT", 12, 20, 16*2 ],
# [ "Content3_TC", "Noto_Sans_TC_Bold", "TA_LEFT", 12, 20, 16*2 ]

# TA_LEFT = 0
# TA_CENTER = 1
# TA_RIGHT = 2
# TA_JUSTIFY = 4

# A4.w = 468

Image = [
        [
            
        ]
    ]

Table = [
        [   
            {"colWidths":None, "rowHeights":None, "splitByRow":1, "repeatRows":22, "repeatCols":0, "rowSplitRange":None, "spaceBefore":12, "spaceAfter":12, "cornerRadii":None},
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # 置中對齊
            ("FONTNAME", (0, 0), (-1, -1), "Noto_Sans_TC_Regular"),  # 字體
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # 上下置中
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor(0x000000) ),  # 框線黑色，寬度0.5
        ],
        [
            {"colWidths":None, "rowHeights":None, "splitByRow":1, "repeatRows":0, "repeatCols":0, "rowSplitRange":None, "spaceBefore":None, "spaceAfter":None, "cornerRadii":None},
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F2B705")),  # 表头背景颜色
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),  # 向左對齊
            ("FONTNAME", (0, 0), (-1, -1), "Noto_Sans_TC_Regular"),  # 字體
            ("FONTSIZE", (0, 0), (-1, -1), 12),  # 表头字体大小
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # 上下置中
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor(0x000000)),  # 框線黑色，寬度0.5
        ]
    ]

# Table(data, colWidths=None, rowHeights=None, style=None, splitByRow=1, repeatRows=0, repeatCols=0, rowSplitRange=None, spaceBefore=None, spaceAfter=None, cornerRadii=None)

# Table(
#     data[1],
#     style=tableStyle,
#     colWidths=[80, (self.pdf.width - 80) ],
#     rowHeights=22,
#     spaceBefore=12,
#     # spaceAfter=12,
# ) 

# Table(
#     data[1],
#     style=tableStyle,
#     colWidths=self.pdf.width / len(data[1][0]),
#     spaceBefore=12,
#     spaceAfter=12,
# )

# https://docs.reportlab.com/reportlab/userguide/ch7_tables/#tabledata-colwidthsnone-rowheightsnone-stylenone-splitbyrow1-repeatrows0-repeatcols0-rowsplitrangenone-spacebeforenone-spaceafternone-cornerradiinone