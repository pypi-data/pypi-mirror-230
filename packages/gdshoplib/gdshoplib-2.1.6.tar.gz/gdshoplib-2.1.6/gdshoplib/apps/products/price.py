from gdshoplib.core.settings import PriceSettins
from gdshoplib.services.gdshop.gdshop import DB

price_settings = PriceSettins()


class Price:
    def __init__(self, product):
        self.product = product
        self._db_request = None

    @property
    def raw(self):
        if not self._db_request:
            self._db_request = DB().get_price(self.product.sku)
        return self._db_request

    @property
    def current_discount(self):
        return int(self.raw["discount"])
        # TODO
        # Получить текущую скидку
        return 100 - round(self.now / self.profit * 100)

    @property
    def now(self):
        return int(self.raw["full_price"])
        discount = self.get_score()
        if discount:
            _now = self.profit + self.profit * (discount * 0.01)
            if _now < self.neitral:
                return self.neitral
            return _now

        return self.profit

    @property
    def eur(self):
        # Цена в EUR
        return self.product.price_eur

    @property
    def net(self):
        # Цена в рублях
        return self.eur * price_settings.EURO_PRICE

    @property
    def gross(self):
        # Цена с учетом расходов и налогов на закупку
        return int(self.raw["base_price"])

    @property
    def neitral(self):
        # Цена безубыточности
        return int(self.raw["base_price"])

    @property
    def profit(self):
        return int(self.raw["profit"])

    def __getitem__(self, key):
        try:
            return super(Price, self).__getattribute__(key)
        except AttributeError:
            return self.__getattr__(key)
