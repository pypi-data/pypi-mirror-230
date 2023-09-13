from pydantic import BaseModel
"""
web参数 校验工具类
"""


class PLUGIN_BASE_MODEL(BaseModel):
    version: str
    type: str
    body: dict
