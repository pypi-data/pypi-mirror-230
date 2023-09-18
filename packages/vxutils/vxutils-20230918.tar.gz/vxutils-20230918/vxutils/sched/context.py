"""引擎上下文context类"""


from collections.abc import MutableMapping, Mapping, Sequence
from pathlib import Path
from typing import Dict, Any, List, Union
from functools import singledispatch
from vxutils.convertors import to_json, vxJSONEncoder, save_json
from vxutils.collections import vxDict

try:
    import simplejson as json
except ImportError:
    import json

__all__ = ["vxContext"]


class vxContext(vxDict):
    def __init__(
        self, config_file: Union[str, Path] = None, settings=None, params=None, **kwargs
    ):
        settings = settings or {}
        params = params or {}
        super().__init__(settings=settings, params=params, **kwargs)

        if config_file:
            self.load_json(config_file)

    def __len__(self) -> int:
        return len(self.params) + len(self.settings) - 2 + len(self.data)

    def __contains__(self, key):
        return any(key in self.data, key in self.params, key in self.settings)

    @property
    def params(self):
        return self.data.setdefault("params", vxDict())

    @property
    def settings(self):
        return self.data.setdefault("settings", vxDict())

    @classmethod
    def load_json(cls, config_file: Union[str, Path]):
        config_file = Path(config_file)
        if not config_file.exists():
            raise OSError(f"config_file({config_file.as_posix()}) is not exists.")

        with open(config_file.as_posix(), "r", encoding="utf-8") as fp:
            config = json.load(fp)
            settings = config.get("settings", {})
            params = config.get("params", {})

        context = cls()
        context.settings.update(settings)
        context.params.update(params)
        return context

    def save_json(self, config_file: Union[str, Path]):
        config = {
            "settings": self.settings,
            "params": self.params,
        }
        save_json(config, config_file)


@vxJSONEncoder.register(vxContext)
def _(obj):
    return {"settings": obj.settings, "params": obj.params}
    # return dict(obj.items())


Mapping.register(vxContext)


if __name__ == "__main__":
    context = vxContext()
    context.hello = "world"
    context.params.id = 1
    context.params.name = "test"
    print(context.params)
    context.settings.id = 1
    context.settings.name = "test"
    print(context)
    context.save_json("log/config.json")
    print(len(context))
