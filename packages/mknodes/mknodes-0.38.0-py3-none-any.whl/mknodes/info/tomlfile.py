from __future__ import annotations

import tomllib

import tomli_w

from mknodes.info import configfile


class TomlFile(configfile.ConfigFile):
    multiline_strings = False

    @classmethod
    def _dump(cls, data: dict) -> str:
        return tomli_w.dumps(data, multiline_strings=cls.multiline_strings)

    @classmethod
    def _load(cls, data: str) -> dict | list:
        return tomllib.loads(data)


if __name__ == "__main__":
    info = TomlFile("pyproject.toml")
    text = info.get_section_text("tool", "hatch", keep_path=True)
    print(text)
