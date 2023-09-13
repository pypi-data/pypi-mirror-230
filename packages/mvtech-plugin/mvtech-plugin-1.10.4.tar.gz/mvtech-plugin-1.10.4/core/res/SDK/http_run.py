try:
    from .web import Server
    from .base import log
except Exception:
    from web import Server
    from base import log


def run(data: dict, plugin_object):
    """
    #   运行功能的整个流程
    参数说明：
    data:dict,      #   运行功能时的必要的json数据
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）

    """

    log("info", "尝试获取数据中的 body")

    #   必要的参数位于data内的body下
    data_body = data.get("body")
    if not data_body:
        log("error", "body 为空")
        return

    log("info", "检测需要运行的组件")
    #   检查json数据是使用在哪个组件上的
    if data_body.get("action"):
        runAction(data_body["action"], data_body, plugin_object)

    elif data_body.get("trigger"):
        runTrigger(data_body["trigger"], data_body, plugin_object)
 

    else:
        log("info", "未检测到需要运行的组件")


def runAction(action_name: str, data: dict, plugin_object):
    """
    #   运行动作
    参数说明：
    action_name:str,    #动作名
    data:dict,      #   运行功能时的必要的数据
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）

    出现异常时，会将异常信息放入log，但不会抛出异常
    """
    log("info", "运行 动作(Action) 中")

    #   根据动作名在插件根目录下的 main.py 文件内的动作列表内选取对应的动作类，并初始化一个对象
    action = plugin_object.actions[action_name]
    #   获取连接器数据
    adapter_data = data.get("adapter_data")
    #   获取入参
    input_data = data.get("input_data")
    #   获取系统通用配置
    base_model = data.get("baseRunModel")

    action._run(input_data, adapter_data, base_model)

    log("info", "动作(Action) 运行结束")


def runTrigger(trigger_name: str, data: dict, plugin_object):
    """
    #   运行触发器
    参数说明：
    action_name:str,    #动作名
    data:dict,      #   运行功能时的必要的数据
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）

    出现异常时，会将异常信息放入log，但不会抛出异常
    """
    log("info", "运行 触发器(Trigger) 中")

    enable_web = data.get("enable_web")

    #   使用web服务
    if enable_web:

        server = Server(plugin_object)
        server.runserver()

    else:
        #   根据动作名在插件根目录下的 main.py 文件内的动作列表内选取对应的动作类，并初始化一个对象
        trigger = plugin_object.triggers[trigger_name]

        adapter_data = data.get("adapter")

        input_data = data.get("input")

        # dispatcher_url = data.get("dispatcher").get("url")
        next_step = data.get("nextStep")

        trigger._run(input_data, adapter_data, next_step)

    log("info", "触发器(Trigger) 运行结束")


def test(data: dict, plugin_object):
    """
    #   只运行连接器部分
    参数说明：
    data:dict,      #   运行功能时的必要的json数据
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）
    """
    #   必要的参数位于data内的body下
    data_body = data.get("body", {})
    adapter_data = data_body.get("adapter")

    #   检查json数据是使用在哪个组件上的
    if data_body.get("action"):
        action_name = data_body["action"]
        action = plugin_object.actions[action_name]
        action._test(adapter_data)

    elif data_body.get("trigger"):
        trigger_name = data_body["trigger"]
        trigger = plugin_object.triggers[trigger_name]
        trigger._test(adapter_data)

    elif data_body.get("alarm"):
        alarm_name = data_body["alarm"]
        alarm = plugin_object.alarm_receivers[alarm_name]
        alarm._test(adapter_data)

    elif data_body.get("receiver"):
        receiver_name = data_body["receiver"]
        receiver = plugin_object.indicator_receivers[receiver_name]
        receiver._test(adapter_data)


def http(plugin_object):
    """
    #   启动rest服务接口
    参数说明：
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）
    """
    server = Server(plugin_object)
    server.runserver()
