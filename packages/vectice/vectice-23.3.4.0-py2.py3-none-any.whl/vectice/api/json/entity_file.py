from __future__ import annotations


class EntityFileOutput(dict):
    @property
    def file_name(self) -> str:
        return str(self["fileName"])
