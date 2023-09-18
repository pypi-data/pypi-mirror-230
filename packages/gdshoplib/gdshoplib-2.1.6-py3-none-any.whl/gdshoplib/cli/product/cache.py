import time
from datetime import datetime
from multiprocessing import Pool
from typing import List, Optional

import typer

from gdshoplib.apps.products.product import Product
from gdshoplib.apps.uploader.uploader import Uploader
from gdshoplib.core.ecosystem import Ecosystem
from gdshoplib.core.settings import NotionSettings
from gdshoplib.packages.cache import KeyDBCache
from gdshoplib.services.notion.database import Database
from gdshoplib.services.notion.notion import Notion

app = typer.Typer()


@app.command()
def clean(id: Optional[str] = typer.Option(None)):
    # TODO: сделать удаление по ID
    KeyDBCache().clean(r"[blocks|pages|databases]*")


@app.command()
def listen(topic: List[str]):
    for message in KeyDBCache().subscribe(topic):
        print(message)


@app.command()
def upload(page_id: Optional[str] = typer.Option(None), infinity: bool = False):
    uploader = Uploader(NotionSettings().KAFKA_TOPIC)
    notion = Notion()

    last_edited = None
    new_time = None
    while True:
        _itarator = notion.search()

        if page_id:
            _itarator = [Notion().get_page(page_id)]

        for page in _itarator:
            page_last_edited = datetime.strptime(
                page["last_edited_time"].split(".")[0], "%Y-%m-%dT%H:%M:%S"
            )
            if not last_edited:
                last_edited = page_last_edited

            if infinity and page_last_edited <= last_edited:
                break

            uploader.send(page)

            for block in notion.get_blocks_iterator(page["id"]):
                uploader.send(block, parent=page["id"])

            if page_last_edited > last_edited:
                new_time = page_last_edited

        if new_time:
            last_edited = new_time
            new_time = None

        time.sleep(1)

        if not infinity:
            break


@app.command()
def scan():
    result = {"all": []}

    for page in Notion().all():
        if not result.get(page["object"]):
            result[page["object"]] = []

        result[page["object"]].append(page["id"])
        result["all"].append(page["id"])

    Ecosystem().send_message(
        NotionSettings().KAFKA_TOPIC, data=result, message_type="scan"
    )


@app.command()
def warm(
    only_exists: bool = typer.Option(False),
    single: bool = typer.Option(False),
    only_edited: bool = typer.Option(True),
    sku: Optional[str] = typer.Option(None),
    loop_iteration: Optional[int] = typer.Option(None),
):
    while True:
        if sku:
            cache_warm_func(Product.get(sku).id)
            return

        if single:
            with Database(
                Product.SETTINGS.PRODUCT_DB, notion=Notion(caching=True)
            ) as database:
                params = {}
                if only_edited and database.get_update_time():
                    print(f"Фильтрация от даты: {database.get_update_time()}")
                    params = database.edited_filter()

                for product in database.pages(params=params):
                    skipped = False
                    if only_exists:
                        if KeyDBCache().exists(product["id"]):
                            print(f"{product['id']}: SKIPPED")
                            skipped = True

                    if not skipped:
                        cache_warm_func(product["id"])
        else:
            with Pool(3) as p:
                with Database(
                    Product.SETTINGS.PRODUCT_DB, notion=Notion(caching=True)
                ) as database:
                    params = {}
                    if only_edited and database.get_update_time():
                        print(f"Фильтрация от даты: {database.get_update_time()}")
                        params = database.edited_filter()

                    for product in database.pages(params=params):
                        skipped = False
                        if only_exists:
                            if KeyDBCache().exists(product["id"]):
                                print(f"{product['id']}: SKIPPED")
                                skipped = True

                        if not skipped:
                            p.apply_async(cache_warm_func, (product["id"],))
                p.close()
                p.join()

        if loop_iteration:
            print("-" * 20)
            time.sleep(loop_iteration)
        else:
            break


@app.command()
def count():
    print(KeyDBCache().count())


@app.command()
def check(single: bool = typer.Option(False)):
    if single:
        for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
            cache_check_action(product["id"])
    else:
        with Pool(3) as p:
            for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
                p.apply_async(cache_check_action, (product["id"],))
            p.close()
            p.join()


#####


def cache_check_action(id):
    for block in Notion().get_blocks(id):
        exists = KeyDBCache().exists(block["id"])
        print(f"{block['id']}: {exists}")


def cache_warm_func(id):
    product = Product(id)
    try:
        product.warm()
    except AttributeError:
        print(f"!= Пропущено {product.sku}: {product.last_edited_time}")
    else:
        print(f"{product.sku}: {product.last_edited_time}")


# if __name__ == "__main__":
#     app()
