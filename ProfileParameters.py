__author__ = 'steinarruneeriksen'

from MarketEnums import *
class ProfileParameters():

    def __init__(self):
        self.assetClass=ASSETCLASSES[AssetClass.DR]
        self.category=ASSETCATEGORIES[AssetCategory.CONSUMPTION]
        self.renewability=True
        self.rampUpRate=0
        self.rampDownRate=0
