from dataclasses import dataclass
import logging


LOGGER_FORMATER = logging.Formatter('[%(asctime)-5s] %(threadName)s - %(levelname)s - %(message)s')

_logger = logging.getLogger("Wallet")
__sh = logging.StreamHandler()
__sh.setFormatter(LOGGER_FORMATER)
_logger.addHandler(__sh)

class amount:

    total: float
    asset_id: str

    def __init__(self, asset_id: str, total: float = 0) -> None:
        self.total = total
        self.asset_id = asset_id

    def __add__(self, other):
        self.total += other
        return self

    def __sub__(self, other):
        self.total -= other
        return self

    def __str__(self) -> str:
        return f'{self.asset_id} : {self.total}'

class InsufficientFundsError(Exception):

    asset_id: str
    difference: float
    available_total: float
    expected_total: float

    def __init__(self, available: amount, expected: amount) -> None:
        self.asset_id = available.asset_id
        self.available_total = available.total
        self.expected_total = expected.total
        self.difference = self.available_total - self.expected_total
        super().__init__(f'The wallet does not have '
                         f'{self.expected_total} units of asset {self.asset_id}, '
                         f'it contains {self.available_total}')
 
class wallet:

    content: dict
    id: str

    def __init__(self, id: str) -> None:
        self.content = {}
        self.id = id

    def __add__(self, _amount: amount) -> None:
        if not isinstance(_amount, (amount,)): 
            raise TypeError(f'Can\'t add {_amount.__class__.__name__}, it must be an amount')
        if  _amount.total < 0: _logger.warning('Using negative numbers in add operation may lead to unexpected behaviours.')
        self.content[_amount.asset_id] = self.get(_amount.asset_id) + _amount.total

    def __sub__(self, _amount: amount) -> None:
        if not isinstance(_amount, (amount,)): 
            raise TypeError(f'Can\'t sub {_amount.__class__.__name__}, it must be an amount')
        if  _amount.total < 0: _logger.warning('Using negative numbers in sub operation may lead to unexpected behaviours.')
        if not self.contains(_amount):
            raise InsufficientFundsError(self.get(_amount.asset_id), _amount)
        self.content[_amount.asset_id] -= _amount.total
    
    def contains(self, _amount: amount) -> bool:
        available: amount = self.content.get(_amount.asset_id)
        if not available:
            return False
        if not _amount.total:
            return True
        if available.total < _amount.total:
            return False
        return True

    def get(self, asset_id: str) -> amount:
        if not self.contains(amount(asset_id)):
            return amount(asset_id)
        return self.content[asset_id]

    def __str__(self) -> str:
        amount_str_list = [str(_amount) for _amount in self.content.values()]
        amount_descriptions = ','.join(amount_str_list)
        return f'Wallet {self.id}[{amount_descriptions}]'

class Wallet:

    def __init__(self) -> None:
        self.__assets = {}

    def __setitem__(self, __k, __v) -> None:
        if not isinstance(__v, (float, int)):
            raise TypeError('This wallet only accept floating points or integers')
        self.__assets[__k] = Asset(__v)

    def __getitem__(self, __k) -> float:
        return self.__assets.get(__k, 0)

class InsufficientAssetError(Exception):

    def __init__(self, available: float, expected: float) -> None:
        super().__init__(f'Insufficient funds. {available} < {expected}')

@dataclass(order=True)
class Asset(float):

    def __init__(self, __v) -> None:
        if __v < 0:
            raise ValueError(f"A wallet can't hold negative values")
        super().__init__()

    def __sub__(self, __x) -> float:
        if float(self) < __x:
            raise InsufficientAssetError(self, __x)
        return super().__sub__(__x)

    def __add__(self, __x) -> float:
        if __x < 0:
            return self.__sub__(-__x)
        return super().__add__(__x)

    def __mul__(self, __x: float) -> float:
        return Asset(float(self) * __x)

w = Wallet()
w['BTC'] += 6
w['BTC'] += -5
a = w['BTC']
a *= 5
print(type(a))
