import sqlite3


class DataBase:
    def __init__(self, file: str):
        self.fullFile = file
        self.file = file.split(".")
        self.fileName = self.file[0]
        self.fileFormat = self.file[-1]

        if self.fileFormat == "sql":
            con = sqlite3.connect(f"{self.fileName}.db")
            cur = con.cursor()
            with open(file) as infile:
                sql = infile.read().split(";")
                for i in sql:
                    cur.execute(i)
                    con.commit()

        elif self.fileFormat == "db":
            self.con = sqlite3.connect(self.fullFile, check_same_thread=False)
            self.cur = self.con.cursor()

    def __str__(self):
        return (self.fileName + self.fileFormat)

    def __repr__(self):
        return (self.fileName + self.fileFormat)

    def runSQL(self, command):
        res = self.cur.execute(command)
        self.con.commit()
        return res.fetchall()
