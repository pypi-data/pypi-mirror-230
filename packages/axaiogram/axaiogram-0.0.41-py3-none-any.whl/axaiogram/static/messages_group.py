import json
from pathlib import Path
from typing import Any, Dict, Union

from pydantic import BaseModel


class MessagesGroup(BaseModel):
    path: str
    lang_code: Union[str, None] = None

    @classmethod
    def from_file(cls, lang_code: Union[str, None] = None):
        path = Path(cls.path)

        messages: Dict[str, Any] = cls.__get_messages(path, lang_code)
        messages["lang_code"] = lang_code

        return cls(**messages)

    @classmethod
    def __get_messages(cls, path, lang_code):
        with open(path, "r") as f:
            messages: Dict[str, Any] = json.load(f)

        _messages = {}

        for key in cls.__fields__.keys():
            if key != "lang_code":
                values: Union[Dict[str, Any], str, None] = messages.get(key)

                if values is None:
                    raise NotImplementedError(f"key `{key}` not fould in file `{path}`")

                if lang_code is not None:
                    cls.__get_from_lang(key, values, lang_code, path, _messages)
                else:
                    _messages[key] = values

        return _messages

    @classmethod
    def __get_from_lang(
        cls,
        key: str,
        value: Dict[str, Any],
        lang_code: str,
        path: Path,
        messages: dict,
    ):
        if type(value) is dict:
            langs = value.get("lang")

            if langs is not None and type(langs) is dict:
                lang = langs.get(lang_code)

                if lang is None:
                    raise NotImplementedError(
                        f"lang_code `{lang_code}` is not found in key `{key}` file `{path}`"
                    )
                messages[key] = lang

                return

        raise NotImplementedError(f"key `{key}` not contains lang param")
