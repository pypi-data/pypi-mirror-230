from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak

# 定義報告書樣式
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))

# 定義報告書內容
title = "標題"
author = "作者"
date = "2023-07-24"

# 創建 PDF 文件
filename = "example.pdf"
doc = SimpleDocTemplate(filename, pagesize=letter,
                        rightMargin=72, leftMargin=72,
                        topMargin=72, bottomMargin=72)

# 建立報告書內容
story = []

# 添加報告書標題
story.append(Spacer(1, 0.25 * inch))
formatted_title = "<b><u>{}</u></b>".format(title)
story.append(Paragraph(formatted_title, styles["Title"]))
story.append(Spacer(1, 0.5 * inch))

# 添加作者和日期
formatted_author = "<b>作者:</b> {}".format(author)
formatted_date = "<b>日期:</b> {}".format(date)
author_date = "{}<br/>{}".format(formatted_author, formatted_date)

story.append(Paragraph(author_date, styles["Normal"]))
story.append(Spacer(1, 0.25 * inch))

# 添加報告書內容
story.append(Paragraph("這是第一頁的內容。", styles["Normal"]))
story.append(Spacer(1, 0.25 * inch))

# 在第一頁結束時插入分頁符號，開啟新頁面
story.append(PageBreak())

# 添加新頁面的內容
story.append(Paragraph("這是第二頁的內容。", styles["Normal"]))
story.append(Spacer(1, 0.25 * inch))

# 生成 PDF 文件
doc.build(story)