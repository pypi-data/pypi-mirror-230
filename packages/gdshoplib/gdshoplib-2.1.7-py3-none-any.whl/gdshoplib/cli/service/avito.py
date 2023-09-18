from datetime import datetime

import typer

from gdshoplib.core.ecosystem import Ecosystem
from gdshoplib.services.avito.avito import Avito

app = typer.Typer()


@app.command()
def access_code():
    print(Avito().get_access_token())


@app.command()
def upload():
    ecosystem = Ecosystem()
    for message in Avito().get_statistic():
        ecosystem.send_message("avito", data=message, message_type="stats")


# if __name__ == "__main__":
#     app()
