import psycopg2
from loguru import logger
from psycopg2 import extras

from gdshoplib.core.settings import DBSettings


class GDShop:
    # Класс для работы с данными из сервисов gdshop
    ...


class DB:
    def __init__(self, data=None):
        self.data = data
        self.settings = DBSettings()

    def execute(func):
        def wrap(self, *args, **kwargs):
            with psycopg2.connect(self.settings.DB_DSB) as conn:
                with conn.cursor(cursor_factory=extras.DictCursor) as curs:
                    query = func(self, *args, **kwargs)
                    try:
                        curs.execute(query)
                        data = curs.fetchall()
                        if not data:
                            logger.warning(f"Запись не найдена: {query}")
                            raise DBNotFound
                        return data[0]
                    except psycopg2.Error as e:
                        logger.error(query)
                        logger.exception(e)
                        raise e

        return wrap

    @execute
    def get_price(self, sku):
        return f"select full_price, base_price, discount, profit from v1.prices p where sku = '{sku}';"


class DBNotFound(Exception):
    ...
