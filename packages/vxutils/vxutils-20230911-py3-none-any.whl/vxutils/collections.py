"""类型集合"""
import contextlib
from pathlib import Path
from typing import Any, List, Union
from functools import singledispatch
from collections import UserDict
from collections.abc import MutableMapping, Sequence, Mapping
from vxutils.convertors import vxJSONEncoder, to_json

try:
    import simplejson as json
except ImportError:
    import json


class vxDict(UserDict):
    """引擎上下文context类"""

    def __setattribute__(self, attr: str, value: Any) -> Any:
        if attr == "data":
            self.data = _to_vxdict(value, self.__class__)
        else:
            self.data[attr] = _to_vxdict(value, self.__class__)

    def __getattr__(self, attr: str) -> Any:
        if attr == "data":
            return self.data
        elif attr in self.data:
            return self.data[attr]
        raise AttributeError(f"{self.__class__.__name__} has no attribute {attr}")

    def __eq__(self, __o: MutableMapping) -> bool:
        if len(self) == len(__o):
            with contextlib.suppress(Exception):
                return all(v == __o[k] for k, v in self.items())
        return False

    def __setstate__(self, state) -> None:
        self.__init__(**state)

    def __getstate__(self) -> dict:
        return self.data

    def __str__(self):
        try:
            return f"< {self.__class__.__name__}(id-{id(self)}) : {to_json(self)} >"
        except (TypeError, KeyError) as err:
            logger.info(err)
            return f"< {self.__class__.__name__}(id-{id(self)}) : {self.data} >"

    __repr__ = __str__

    def to_dict(self) -> dict:
        """转换为dict"""
        return {k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in self.items()}

    def update(self, __m: MutableMapping = None, **kwargs) -> None:
        if __m is not None:
            for k, v in __m.items():
                self[k] = _to_vxdict(v, self.__class__)

        for k, v in kwargs.items():
            self[k] = _to_vxdict(v, self.__class__)


@singledispatch
def _to_vxdict(self: Any, obj_cls: type = vxDict) -> vxDict:
    """转换为vxdict obj"""
    return self


@_to_vxdict.register(Mapping)
def _(obj: Mapping, obj_cls: type = vxDict) -> vxDict:
    return obj_cls(**obj)


@_to_vxdict.register(MutableMapping)
def _(obj: MutableMapping, obj_cls: type = vxDict) -> vxDict:
    return obj_cls(**obj)


@_to_vxdict.register(UserDict)
def _(obj: UserDict, obj_cls: type = vxDict) -> vxDict:
    return obj_cls(**obj)


@_to_vxdict.register(dict)
def _(obj: dict, obj_cls: type = vxDict) -> vxDict:
    return obj_cls(**obj)


@_to_vxdict.register(Sequence)
def _(obj: Sequence, obj_cls: type = vxDict) -> List:
    return obj if isinstance(obj, str) else [_to_vxdict(o_, obj_cls) for o_ in obj]


@vxJSONEncoder.register(vxDict)
def _(obj):
    return obj.to_dict()


Mapping.register(vxDict)
MutableMapping.register(vxDict)


class vxContext(vxDict):
    """引擎上下文context类"""

    def __init__(self, default_config: Mapping = None, **kwargs):
        self._default_config = default_config or {}
        config = self._default_config.copy()
        if kwargs:
            config.update(**kwargs)
        super().__init__(**config)

    @classmethod
    def from_json(
        cls, _default_config: Mapping = None, json_file: Union[str, Path] = None
    ) -> "vxContext":
        """从json字符串中加载"""
        with open(json_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            return cls(_default_config, **config)

    def save_json(self, json_file: Union[str, Path], **kwargs):
        """保存为json文件"""
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(
                self, f, ensure_ascii=False, cls=vxJSONEncoder, indent=4, **kwargs
            )


Mapping.register(vxContext)
MutableMapping.register(vxContext)


if __name__ == "__main__":
    from vxutils import logger

    d = vxContext(default_config={"x": 1, "y": 2, "z": 3}, a=1, b={"e": 4, "f": 5}, c=3)
    logger.info(d)
    d.update(**{"a1": 2, "b1": {"e": 5, "f": 6}, "c1": 4})
    logger.info(d.data)

    # logger.info(d.to_dict())
    # logger.info("e" in d.keys())
    # logger.info(isinstance(d, dict))
    # d.update({"a1": 2, "b1": {"e": 5, "f": 6}, "c1": 4})
    # logger.info(d)
    # logger.info(d.keys())
    # logger.info(d.a1)
    # logger.info(d.b1.e)
    # logger.info(isinstance(d, UserDict))
    # logger.info(f"{round(400000 / 680)*1000*11.50*0.5:,.2f}")
