from nonebot import get_driver
from pydantic import BaseModel


class Config(BaseModel):
    web_user: str = "admin"
    web_passwd: str = "passwd"
    web_host: str = "127.0.0.1"
    web_port: int = 8666


config = Config.parse_obj(get_driver().config)
