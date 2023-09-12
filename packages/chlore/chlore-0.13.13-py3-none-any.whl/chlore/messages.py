import typing
from fastapi import Request
from enum import IntEnum
from dataclasses import dataclass


class FlashType(IntEnum):
    DEBUG = 0
    INFO = 1
    SUCCESS = 2
    WARNING = 3
    ERROR = 4


@dataclass
class UiFlashMessage:
    "Represent a flash message, with the purpose of rendering in jinja"

    message: str
    category: FlashType

    @property
    def bootstrap_classes(self):
        match self.category:
            case FlashType.SUCCESS:
                return "bg-success bg-opacity-50"
            case FlashType.ERROR:
                return "bg-danger bg-opacity-50"
            case FlashType.WARNING:
                return "bg-warning bg-opacity-50"
            case _:
                return ""


def add_message(request: Request, category: FlashType, message: str) -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})


def get_messages(request: Request):
    return request.session.pop("_messages") if "_messages" in request.session else []


class FlashMessages:
    def __init__(self, request: Request):
        self.request = request

    def add(self, category: FlashType, message: str):
        return add_message(self.request, category, message)

    def pop_all(self):
        return [UiFlashMessage(**m) for m in get_messages(self.request)]

    def debug(self, message: str):
        self.add(FlashType.DEBUG, message)

    def info(self, message: str):
        self.add(FlashType.INFO, message)

    def success(self, message: str):
        self.add(FlashType.SUCCESS, message)

    def warning(self, message: str):
        self.add(FlashType.WARNING, message)

    def error(self, message: str):
        self.add(FlashType.ERROR, message)

    @classmethod
    def __call__(cls, request: Request):
        "Small hack: make this Class a fastapi dependable."
        return FlashMessages(request)
