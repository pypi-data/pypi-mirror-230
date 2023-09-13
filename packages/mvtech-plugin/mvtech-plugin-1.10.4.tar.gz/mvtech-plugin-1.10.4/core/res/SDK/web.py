from fastapi import FastAPI
import typing
import uvicorn
import asyncio
import threading
# from uvicorn import demo_constants, Server
try:
    from . import models
    from .base import clearLog, checkModel, log, getLog, checkTriggerModel
    from .service_stop import start_live, live_add, live_sub
except Exception:
    import models
    from base import clearLog, checkModel, log, getLog, checkTriggerModel
    from service_stop import start_live, live_add, live_sub



app = FastAPI(title="MVTECH",
              version="0.0.1",
              description="自写sdk, 增加 test接口可以测试适配器，适配器并不为单例的，第一执行的组件")
PORT = 8888
# web 调用　自写方法　关键
plugins = None
# uvicorn.Server 
userver = None 
@staticmethod
def getServer() -> uvicorn.Server :
    global userver
    return userver

class Server(object):

    def __init__(self, plus):

        global plugins
        plugins = plus

    @staticmethod
    @app.get("/info")
    def getInfos():
        logInfo = getLog()
        if "异常" in logInfo or "错误" in logInfo :
            return {"code":500,"success": False,"log": logInfo}
        else:
            return {"code":200,"success": True,"log": ''}

    @staticmethod
    @app.post("/actions/{action_name}")
    def actions(
            action_name,
            plugin_stdin: typing.Optional[models.PLUGIN_BASE_MODEL] = None):
        live_add()
        try:
            clearLog()

            action = plugins.actions[action_name]

            # 取出body
            data = plugin_stdin.dict()
            checkModel(data, models.PLUGIN_BASE_MODEL)
            data_body = data.get("body")

            # 获取input
            input_data = data_body.get("input_data")
            adapter_data = data_body.get("adapter_data")
            baseRunModel = data_body.get("baseRunModel")
            # 执行 外部run 相关操作
            output = action._run(input_data, adapter_data, baseRunModel)
            return output
        finally:
            live_sub()
        

    @staticmethod
    @app.post("/actions/{action_name}/test")
    def actions_test(
            action_name: str,
            plugin_stdin: typing.Optional[models.PLUGIN_BASE_MODEL] = None):

        clearLog()

        action = plugins.actions[action_name]

        # 取出body
        data = plugin_stdin.dict()
        checkModel(data, models.PLUGIN_BASE_MODEL)
        data_body = data.get("body")

        # 获取input
        adapter_data = data_body.get("adapter_data")

        output = action._test(adapter_data)

        return output

    @staticmethod
    @app.post("/triggers/{trigger_name}")
    async def triggers(trigger_name: str,
                 plugin_stdin: typing.Optional[models.PLUGIN_BASE_MODEL]):

        clearLog()

        # 外部类
        trigger = plugins.triggers[trigger_name]

        # 取出body
        data = plugin_stdin.dict()
        checkTriggerModel(data, models.PLUGIN_BASE_MODEL)
        data_body = data.get("body")

        # 获取input
        input_data = data_body.get("input_data")
        adapter_data = data_body.get("adapter_data")
        next_step = data_body.get("nextStep")
        # 执行　外部run 相关操作
        coroutine1 = trigger._run(input_data, adapter_data, next_step)  # 调用async 异步方法 
        new_loop = asyncio.new_event_loop()
        t = threading.Thread(target=Server.start_loop, args=(new_loop,))  # 通过当前线程开启新的线程去启动事件循环
        t.start()
        asyncio.run_coroutine_threadsafe(coroutine1, new_loop)  # 这几个是关键，代表在新线程中事件循环不断“游走”执行
        # output = trigger._run(input_data, adapter_data, next_step)
        # trigger._run(input_data, adapter_data, next_step)
        # asyncio.run(trigger._run(input_data, adapter_data, next_step))
        
        # t1 = threading.Thread(target=Server.test_task(trigger,input_data, adapter_data, next_step))
        # # t1.setDaemon(True)
        # t1.start()
        output = {"code":200,"success": True,"log": getLog()}
        return output

    @staticmethod
    @app.post("/triggers/{trigger_name}/test")
    def trigger_test(
            trigger_name: str,
            plugin_stdin: typing.Optional[models.PLUGIN_BASE_MODEL] = None):

        clearLog()

        # 外部类
        trigger = plugins.triggers[trigger_name]

        # 取出body
        data = plugin_stdin.dict()
        checkModel(data, models.PLUGIN_BASE_MODEL)
        data_body = data.get("body")

        # 获取input
        adapter_data = data_body.get("adapter_data")

        output = trigger._test(adapter_data)

        return output

    def runserver(self):
        portV = 8888
        log("info", f"mvtech web start  http://0.0.0.0:{portV}/docs#")
        # config = uvicorn.Config(app, host="127.0.0.1", port=portV, log_level="info", loop="asyncio")
        ser_config = uvicorn.Config(app, host="0.0.0.0", port=portV, log_level="info")
        global userver
        userver = uvicorn.Server(config=ser_config) 
        # start_live(userver)
        userver.run()
               

         
