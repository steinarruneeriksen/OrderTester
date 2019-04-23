__author__ = 'steinarruneeriksen'



class TimeParameters():

    def __init__(self, periodFrom, periodUntil):
        self.blockSizeInSeconds=int((periodUntil-periodFrom).total_seconds())
        self.periodFromUtc=periodFrom.isoformat()
        self.periodUntilUtc=periodUntil.isoformat()
        self.maxBlocks=1
        self.adjacentBlocks=1
        self.restBlocks=0
