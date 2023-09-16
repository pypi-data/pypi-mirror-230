from ..basic.BasisDay import BasisDay

class DataVis(BasisDay):
    def __init__(self):
        super().__init__( "vis" )

    def inFile(self):
        self.loadDir( [self.inPath] )
    
    def toFile(self):
        self.loadDir( [self.toPath] )