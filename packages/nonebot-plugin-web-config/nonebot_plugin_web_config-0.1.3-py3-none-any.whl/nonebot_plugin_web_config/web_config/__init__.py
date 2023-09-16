import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from .util import decode_json

Root = Path() / "data" / "WebUiConfig"
Root.mkdir(parents=True, exist_ok=True)

Instances = {}


class WebUiConfigModel(BaseModel):
    __type__: Literal["dict", "list-dict"] = "dict"
    __config_name__ = None
    __slots__ = "__store_path__"

    def __init__(self):
        if not self.__store_path__.exists():
            self.save()
        with self.__store_path__.open() as file:
            data = decode_json(json.load(file))
        super().__init__(**data)

    def __init_subclass__(cls, **kwargs):
        cls.__store_path__: Path = Root / cls.__module__.split(".")[0] / f"{cls.__name__}.json"
        cls.__store_path__.parent.mkdir(parents=True, exist_ok=True)
        if cls.__config_name__ is None:
            setattr(cls, "__config_name__", cls.__name__)
        if cls.__type__ == "list-dict":
            if not hasattr(cls, "data_dict"):
                raise Exception("list-dict类config只能有一个data_dict属性供使用")

    def save(self):
        data = decode_json(self.dict())
        self.__store_path__.touch(exist_ok=True)
        with self.__store_path__.open("w") as f:
            json.dump(data, f)


def get_instances():
    global Instances
    for subclass in WebUiConfigModel.__subclasses__():
        module_ = str(subclass.__module__).split(".")[0]
        name_ = str(subclass.__config_name__)
        if module_ not in Instances.keys():
            Instances[module_] = {}
        Instances[module_][name_] = subclass()
    return Instances


def get_config(module: str, config_name: str):
    module = str(module).split(".")[0]
    if module not in Instances.keys():
        get_instances()
    if module not in Instances.keys():
        raise Exception("Model not in Web configs.")
    if config_name not in Instances[module].keys():
        raise Exception("Config not in Web configs")
    return Instances[module][config_name]
