import sys
sys.path.append('..')
from ..basic import config
import sqlite3
import pandas as pd

class DataReader:
    # constructor
    def __init__(self, inFile: str, *filetable: str):
        self.inFile = inFile
        self.fileFormat = inFile.split(".")[-1]
        self.filetable = filetable[0] if filetable else ""
        self.df = pd.DataFrame(self.inFile())

    # setter
    # 輸入 數據文件
    def inFile(self):
        if self.fileFormat == "db":
            self.conn = sqlite3.connect(f"{self.inFile}")
            return pd.read_sql_query(
                f"SELECT * FROM {self.filetable}", sqlite3.connect(self.inFile)
            )
        elif self.fileFormat == "csv":
            return pd.read_csv(self.inFile)
        elif self.fileFormat == "json":
            return pd.read_json(self.inFile)
        elif self.inFile == "xlsx":
            return pd.read_excel(self.inFile)
        else:
            return print("input: Does not support ")

    # getter
    # 輸出 數據文件
    def toFile(self, file: str):
        file = file.split(".")
        name = file[0]
        format = file[-1].lower()
        if format == "all":
            self.df.to_csv(f"{name}.csv", index=False)
            self.df.to_json(f"{name}.json")
            self.df.to_excel(f"{name}.xlsx")
        elif format == "csv":
            self.df.to_csv(f"{name}.csv", index=False)
        elif format == "json":
            self.df.to_json(f"{name}.json")
        elif format == "xlsx":
            self.df.to_excel(f"{name}.xlsx")
        elif format == "sql":
            with open(f"{name}.sql", "w") as f:
                for line in self.conn.iterdump():
                    f.write(f"${line}\n")
                self.conn.close()
        else:
            print("output: Does not support")

    # display DataFrame
    def show(self, row=60):
        pd.options.display.max_rows = row
        return self.df

    # display DataFrame all data
    def showAll(self):
        pd.options.display.max_columns = None
        pd.options.display.max_rows = None
        return self.df

    def show_all(self):
        pd.options.display.max_columns = None
        pd.options.display.max_rows = None
        return self.df
    
    # Basic 一般
    def __str__(self) -> str:
        return self.table().to_string()

    def __repr__(self) -> str:
        return self.table().to_string()

    def name(self) -> str:
        return self.inFile

    def format(self) -> str:
        return self.fileFormat

    def table(self) -> pd.core.frame.DataFrame:
        return self.df
