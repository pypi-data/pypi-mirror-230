from datetime import datetime

import typer

from gdshoplib.core.ecosystem import Ecosystem
from gdshoplib.services.avito.avito import Avito
from gdshoplib.services.vk.market import VKMarket
from gdshoplib.services.vk.page import VKPage
from gdshoplib.services.vk.stats import VKStats
from gdshoplib.services.vk.vk import VK

app = typer.Typer()


@app.command()
def access_code(code=None):
    if not code:
        VK().get_oauth_code()
        code = typer.prompt("Код")

    print(VK().get_access_token(code))


@app.command()
def online(active: bool = True):
    if active:
        VKPage().set_enable()
    else:
        VKPage().set_disable()


@app.command()
def health():
    assert VKMarket().list(), "Запрос в VK не выполняется"
    print("OK")


@app.command()
def upload():
    ecosystem = Ecosystem()
    for message in [
        *VKStats().community(),
        *VKStats().products(),
        *VKStats().members(),
    ]:
        ecosystem.send_message("vk", data=message, message_type="stats")


if __name__ == "__main__":
    app()
