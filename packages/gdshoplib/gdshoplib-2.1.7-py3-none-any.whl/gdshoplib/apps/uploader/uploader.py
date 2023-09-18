import hashlib
from datetime import datetime

import ujson as json
from dateutil.parser import parse

from gdshoplib.apps.products.media import ProductMedia, S3File
from gdshoplib.core.ecosystem import Ecosystem
from gdshoplib.packages.s3v2 import File, S3v2
from gdshoplib.services.notion.page import Page


class Uploader:
    ECOSYSTEM = None

    def __init__(self, topic):
        self.topic = topic
        self.accepted_blocks = ("table_row", "image", "code")

    @property
    def ecosystem(self):
        if not self.ECOSYSTEM:
            self.ECOSYSTEM = Ecosystem()
        return self.ECOSYSTEM

    def send(self, message, parent=None):
        if message["object"] == "page":
            for k, value in message["properties"].items():
                if value["type"] == "files":
                    value = {**value, "page_id": message["id"]}

                _message = dict(
                    id=value["id"],
                    title=k,
                    parent_id=message["id"],
                    type=value["type"],
                    content=json.dumps({"content": handlers[value["type"]](value)}),
                )
                self.ecosystem.send_message(f"{self.topic}.property", data=_message)

            _message = dict(
                id=message["id"],
                parent_id=message["parent"][message["parent"]["type"]],
                url=message["url"],
                last_edited_time=handlers["last_edited_time"](message),
                created_time=handlers["created_time"](message),
                author_id=message["created_by"]["id"],
                editor_id=message["last_edited_by"]["id"],
                archived=message["archived"],
            )
            self.ecosystem.send_message(f"{self.topic}.page", data=_message)

        elif message["object"] == "block":
            if message["type"] in self.accepted_blocks:
                _message = dict(
                    id=message["id"],
                    type=message["type"],
                    content=json.dumps({"content": handlers[message["type"]](message)}),
                    has_children=message["has_children"],
                    archived=message["archived"],
                    parent_id=parent or message["parent"][message["parent"]["type"]],
                )

                self.ecosystem.send_message(f"{self.topic}.block", data=_message)
                self.ecosystem.send_message(
                    f"{self.topic}.block.{message['type']}", data=_message
                )


def file_handler(data):
    # Получить ключ файла
    _object = ProductMedia(data["id"])
    key = f'{data["type"]}.{data["id"]}.{datetime.timestamp(parse(data["last_edited_time"]))}.{_object.format}'

    # Сохранить/проверить на S3
    if not S3v2().exists(File(key=key)):
        S3v2().put(File(content=_object.content, key=key, mime=_object.mime))

    return {
        "key": key,
        "caption": handlers["text"](data[data["type"]]["caption"]),
    }


def files_handler(data):
    # Получить ключ файла
    page = Page(data["page_id"])
    result = []

    for ind, file in enumerate(data["files"]):
        _file = S3File(file["file"]["url"])
        _key = f'files.{page.id}.{data["id"]}.{ind}.{datetime.timestamp(parse(page.last_edited_time))}'
        key = f'{hashlib.md5(_key.encode("utf-8")).hexdigest()}.{_file.format}'

        if not S3v2().exists(File(key=key)):
            S3v2().put(File(content=_file.content, key=key, mime=_file.mime))

        result.append(key)
    return result


def table_row_handler(data):
    # TODO: Таблицы собрать все в 1 массив массивов
    result = {"table_id": data["parent"]["block_id"], "cells": []}
    for cell in data["table_row"]["cells"]:
        result["cells"].append(handlers["text"](cell))
    return result


def date_handler(data):
    result = {"start": None, "end": None}
    _date = data["date"]
    if not _date:
        return None

    if _date["start"]:
        result["start"] = datetime.timestamp(parse(_date["start"]))

    if _date["end"]:
        result["end"] = datetime.timestamp(parse(_date["end"]))

    return result


def code_handler(data):
    result = {
        "language": data["code"]["language"],
        "caption": handlers["text"](data["code"]["caption"]),
        "content": handlers["rich_text"](data["code"]),
    }
    return result


handlers = {}

handlers["select"] = lambda data: data["select"] and data["select"]["name"]
handlers["files"] = lambda data: files_handler(data)
handlers["image"] = lambda data: file_handler(data)
handlers["multi_select"] = lambda data: [
    select["name"] for select in data["multi_select"]
]
handlers["last_edited_time"] = lambda data: datetime.timestamp(
    parse(data["last_edited_time"])
)
handlers["created_time"] = lambda data: datetime.timestamp(parse(data["created_time"]))
handlers["date"] = date_handler
handlers["created_by"] = lambda data: data["created_by"]["id"]
handlers["last_edited_by"] = lambda data: data["last_edited_by"]["id"]
handlers["relation"] = lambda data: [r["id"] for r in data["relation"]]
handlers["status"] = lambda data: data["status"]
handlers["url"] = lambda data: data["url"]
handlers["number"] = lambda data: data["number"]
handlers["rich_text"] = lambda data: "".join(
    [text[text["type"]]["content"] for text in data["rich_text"]]
)
handlers["title"] = lambda data: "".join(
    [text[text["type"]]["content"] for text in data["title"]]
)
handlers["text"] = lambda data: "".join([text["plain_text"] for text in data])
handlers["table_row"] = table_row_handler
handlers["code"] = code_handler
handlers["checkbox"] = lambda data: data["checkbox"]
handlers["formula"] = lambda data: data["formula"][data["formula"]["type"]]
handlers["people"] = lambda data: [person["id"] for person in data["people"]]
handlers["unique_id"] = lambda data: data["unique_id"]
