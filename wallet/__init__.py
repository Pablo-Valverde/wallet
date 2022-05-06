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

    def add(self, _amount: amount) -> None:
        if  _amount.total < 0: _logger.warning('Using negative numbers in add operation may lead to unexpected behaviours.')
        self.content[_amount.asset_id] = self.get(_amount.asset_id) + _amount.total

    def sub(self, _amount: amount) -> None:
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

w = wallet(1)
w.add(amount(1, 10))
w.add(amount(1, 20))
w.sub(amount(1, 20))
print(w.contains(amount(1, 5)))
print(w)
