# from pyday import DataReader
# dr = DataReader()
# dr.inFile("")
# dr.toFile("test.csv")

# from pyday import Data2PDF
# d2pdf = Data2PDF()
# d2pdf.inFile("test2.json")
# d2pdf.toFile("test2.pdf")

from pyday import DataVis
dv = DataVis()
dv.inFile("test.json")
dv.toFile("test.png")