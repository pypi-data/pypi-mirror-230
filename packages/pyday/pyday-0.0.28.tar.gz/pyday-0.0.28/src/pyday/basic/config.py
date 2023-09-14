import os

# 獲取 目前腳本pyday所在目錄的父目錄的絕對路徑
basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
worKdir = os.getcwd()

# 字體的絕對路徑
font_path = os.path.join(basedir, "basic/font")
Noto_Sans_TC = os.path.join(font_path, "Noto_Sans_TC")
Noto_Sans_SC = os.path.join(font_path, "Noto_Sans_SC")

font_otf = {
    "Noto_Sans_TC_Black": os.path.join(Noto_Sans_TC, "NotoSansTC-Black.otf"),
    "Noto_Sans_TC_Bold": os.path.join(Noto_Sans_TC, "NotoSansTC-Bold.otf"),
    "Noto_Sans_TC_Light": os.path.join(Noto_Sans_TC, "NotoSansTC-Light.otf"),
    "Noto_Sans_TC_Medium": os.path.join(Noto_Sans_TC, "NotoSansTC-Medium.otf"),
    "Noto_Sans_TC_Regular": os.path.join(Noto_Sans_TC, "NotoSansTC-Regular.otf"),
    "Noto_Sans_TC_Thin": os.path.join(Noto_Sans_TC, "NotoSansTC-Thin.otf"),
    "Noto_Sans_SC_Black": os.path.join(Noto_Sans_SC, "NotoSansSC-Black.otf"),
    "Noto_Sans_SC_Bold": os.path.join(Noto_Sans_SC, "NotoSansSC-Bold.otf"),
    "Noto_Sans_SC_Light": os.path.join(Noto_Sans_SC, "NotoSansSC-Light.otf"),
    "Noto_Sans_SC_Medium": os.path.join(Noto_Sans_SC, "NotoSansSC-Medium.otf"),
    "Noto_Sans_SC_Regular": os.path.join(Noto_Sans_SC, "NotoSansSC-Regular.otf"),
    "Noto_Sans_SC_Thin": os.path.join(Noto_Sans_SC, "NotoSansSC-Thin.otf"),
}
