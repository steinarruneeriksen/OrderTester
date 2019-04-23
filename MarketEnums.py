__author__ = 'steinarruneeriksen'

from enum import Enum

class SideEnum(Enum):
    BUY = 1
    SELL = 2
class QuantityTypeEnum(Enum):
    POWER = 1
    ENERGY = 2
class RegulationEnum(Enum):
    UP = 1
    DOWN = 2
class PriceTypeEnum(Enum):
    LIMIT = 1
    MARKET = 2
class FillTypeEnum(Enum):
    FOK = 1
    FAK = 2
    NORMAL=3
class OrderStatusEnum(Enum):
    ACTIVE = 1
    FILLED = 2
    EXPIRED=3
    CANCELLED=4

class AssetClass(Enum):
    DR = 1
    DG = 2
    PV=3

class AssetCategory(Enum):
    CONSUMPTION = 1
    PRODUCTION = 2


FILLTYPES={
    FillTypeEnum.FOK: 'FOK',
    FillTypeEnum.FAK: 'FAK',
    FillTypeEnum.NORMAL: 'Normal',
}

ASSETCLASSES={
    AssetClass.DR: 'DR',
    AssetClass.DG: 'DG',
    AssetClass.PV: 'PV',
}

ASSETCATEGORIES={
    AssetCategory.CONSUMPTION: 'CONSUMPTION',
    AssetCategory.PRODUCTION: 'PRODUCTION',
}

ORDERSTATUSES={
    OrderStatusEnum.ACTIVE: 'ORDER_ACTIVE',
    OrderStatusEnum.FILLED: 'ORDER_FILLED',
    OrderStatusEnum.EXPIRED: 'ORDER_EXPIRED',
    OrderStatusEnum.CANCELLED: 'ORDER_CANCELLED',
}
SIDES={
    SideEnum.BUY: 'Buy',
    SideEnum.SELL: 'Sell',
}
QUANTITYTYPES={
    QuantityTypeEnum.POWER: 'Power',
    QuantityTypeEnum.ENERGY: 'Energy',
}
REGULATIONS={
    RegulationEnum.DOWN: 'Down',
    RegulationEnum.UP: 'Up',
}
PRICETYPES={
    PriceTypeEnum.MARKET: 'Market',
    PriceTypeEnum.LIMIT: 'Limit',
}