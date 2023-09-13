import json
import logging
import time
import os
import requests
from pydantic import ValidationError
from json import JSONDecodeError
try:
    from . import models
except Exception:
    import models
"""
错误处理以及工具方法
"""

#   日志数据
log_data = ""
suc_start = True

class Tools(object):

    def getAPIUrl(self, ser_url: str, ser_router: str) -> str:
        """
        获取route路由路径
        """
        url = ""
        if not ser_url.endswith('/') and not ser_router.startswith('/'):
            url = ser_url + "/" + ser_router
        else:
            url = ser_url + ser_router
        return url

    def getJwt(self, upSelf, data={}):
        username = data.get("login_param_auth", {}).get("username")
        password = data.get("login_param_auth", {}).get('password')
        jwtUrl = data.get("login_param_auth", {}).get('jwturl')
        url = self.getAPIUrl(upSelf.ser_url, jwtUrl)
        # "{ \"code\": \"0\", \"password\": \"123456\", \"username\": \"admin\", \"uuid\": \"0\"}"
        body = {
            "code": "0",
            "password": password,
            "username": username,
            "uuid": "0"
        }
        try:
            # ,headers={"Content-Type": "application/json"}
            response = requests.post(url, json=body, verify=upSelf.ssl_verify)
        except Exception as error:
            raise Exception(f"请求失败\n  错误原因：{error}")
        try:
            body_object = response.json()
        except Exception:
            body_object = {}
        code = body_object.get("code")
        if code == 400:
            raise Exception(f"请求失败\n  错误原因：{body_object}")
        token = body_object.get("token")
        upSelf.jwt = "JWT " + token
        upSelf.default_headers["Authorization"] = upSelf.jwt
        # print("token :",token)


def checkModel(data: dict, model) -> dict:
    """
    #   根据models.py内的校验数据校验data内的参数是否符合要求，并尽可能返回规范化的数据
    参数说明：
    data:dict,  #   数据
    model,      #   校验数据

    注意：数据校验很重要，校验不通过时该方法应当能够立即中断插件的运行，所以请尽可能不要在try内使用此方法

    pydantic库会尝试去规范化进入的数据，即转换原来的数据至规定的格式
    如，123 -> 123.0 （输入为int，规定为float）， False -> "False" （输入为boolean，规定为str）

    校验失败时抛出异常
    """
    try:
        log("info", f"检查的数据{data}")
        log("info", f"根据 {model.__name__} 校验数据中")

        data = model(**data).json()

        log("info", "校验完成")

        return json.loads(data)

    #   pydantic 会在它正在验证的数据中发现错误时引发 ValidationError
    except ValidationError as errors:
        #   当有多个参数验证不通过时，会有多个错误
        errors = json.loads(errors.json())
        error_log = "数据参数验证不通过"
        for error in errors:
            error_log += f"\n错误参数：{error['loc']}\n错误原因：{error['msg']}"
        log("error", error_log)
        raise Exception(error_log)


# 触发器 模型检查，触发器出现问题，容器就停止
def checkTriggerModel(data: dict, model) -> dict:
    """
    #   根据models.py内的校验数据校验data内的参数是否符合要求，并尽可能返回规范化的数据
    参数说明：
    data:dict,  #   数据
    model,      #   校验数据

    注意：数据校验很重要，校验不通过时该方法应当能够立即中断插件的运行，所以请尽可能不要在try内使用此方法

    pydantic库会尝试去规范化进入的数据，即转换原来的数据至规定的格式
    如，123 -> 123.0 （输入为int，规定为float）， False -> "False" （输入为boolean，规定为str）

    校验失败时抛出异常
    """
    global suc_start
    try:
        log("info", f"检查的数据{data}")
        log("info", f"根据触发器 {model.__name__} 校验数据中")
        data = model(**data).json()

        log("info", "校验完成")

        return json.loads(data)

    #   pydantic 会在它正在验证的数据中发现错误时引发 ValidationError
    except ValidationError as errors:
        log("start_error", errors)
        suc_start = False
        logging.error("\033[91m 启动失败 \033[0m")
        #   当有多个参数验证不通过时，会有多个错误
        errors = json.loads(errors.json())
        error_log = "数据参数验证不通过"
        for error in errors:
            error_log += f"\n错误参数：{error['loc']}\n错误原因：{error['msg']}"
        log("start_error", error_log)
        raise Exception(error_log)
    except Exception as errors:
        log("start_error", errors)
        suc_start = False
        logging.error("\033[91m 启动失败 \033[0m")
        log("start_error", errors)
        raise Exception(error_log)
    

logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s\n  %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


def log(level="debug", msg=""):
    """
    #   设置不同级别的log输出
    参数说明：
    level:str,    #   log等级，levels = debug, info, attention, warning, error, critical
    msg:str,    #   log信息
    """
    global log_data
    global suc_start

    msg = str(msg)
    isStartError = False
    #   输出带颜色log需要执行一次os.system("")
    os.system("")
    # logging.info("levels:"+level)
    if level == "debug":

        logging.debug("\033[32m" + msg + "\033[0m")

    elif level == "info":

        logging.info(msg)

    elif level == "attention":

        logging.info("\033[94m" + msg + "\033[0m")

    elif level == "warning":

        logging.warning("\033[93m" + msg + "\033[0m")

    elif level == "error":

        logging.error("\033[91m" + msg + "\033[0m")

    elif level == "start_error":
        isStartError = True
        logging.error("\033[91m" + msg + "\033[0m")
        

    elif level == "critical":

        logging.critical("\033[91m" + msg + "\033[0m")

    #   时间戳
    log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    log_data += f"[{log_time}] {level.upper()}\n  {msg}\n"
    
    if isStartError:
        suc_start = False
        logging.error("\033[91m 启动失败 \033[0m")
    # else:
        # logging.info("\033[94m 启动成功  \033[0m")

def clearLog():
    """
    #   清空日志
    
    docker内多次运行插件时，会产生大量日志，故需要此方法
    """
    global log_data
    log_data = ""

def getLog() -> str:
    return log_data

def isSucStart() -> bool:
    return suc_start

def loadData(path: str) -> dict:
    """
    #   读取json文件内的数据
    参数说明:
    path:str,   #   json文件路径

    返回dict形式的数据
    读取失败时抛出异常
    """
    try:

        if not os.path.exists(path):
            raise Exception(f"路径错误：\n{path}")

        with open(path, "r", encoding="utf-8") as file:

            data = json.load(file)
            #   校验数据格式
            checkModel(data, models.PLUGIN_BASE_MODEL)

        return data

    except JSONDecodeError:
        raise Exception("json数据文件格式转换错误，请检查json文件的格式")

    except Exception as error:
        raise Exception(f"数据文件 {os.path.basename(path)} 读取失败，原因如下：\n{error}")
