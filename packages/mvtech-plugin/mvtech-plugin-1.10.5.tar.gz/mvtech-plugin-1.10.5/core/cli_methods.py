import os

from core.demo_constants import *
from core.tools import Tools
import logging

tools = Tools()


def generate(path: str, yml: str):
    """
    生成插件
    """

    # 验证路径，　是否是yaml文件
    yml_path = os.path.join(path, yml)
    if not any([yml.endswith(y)
                for y in ["yml", "yaml"]]) or not os.path.exists(yml_path):
        logging.error(f"yaml路径错误 - {yml_path}")
        return
    else:
        yaml_data = tools.readYaml(yml_path)
        logging.info(f"look {yml}")

    plugin_name = yaml_data.get("name", "mvtechname")
    actions_class_list = []
    triggers_class_list = []

    # 当前文件路劲下生成sdk
    tar_path = os.path.join(BASE_DIR, os.path.join("res", "project.tar.gz"))
    target_path = path
    tools.tarExtract(tar_path, target_path)

    # 读取types
    types = yaml_data.get("types")
    typesTemp = ""
    if types:
        for types_name, types_data in types.items():
            typesData = {
                "className": tools.getModelName(types_name),
                "args": tools.ymlTransPy(types_data)
            }
            typesTemp += tools.renderStrTemplate(typesData, MODEL_INFO)

    # 读取adapter
    adapter = yaml_data.get("adapter")
    adapter = {
        "className": tools.getModelName("adapter"),
        "args": tools.ymlTransPy(adapter)
    }
    connTemp = tools.renderStrTemplate(adapter, MODEL_INFO)

    # 创建tests
    tests_path = os.path.join(path, "tests")
    if not os.path.exists(tests_path):
        os.mkdir(tests_path)

    # 生成actions
    actions = yaml_data.get("actions")
    if actions:
        actions_path = os.path.join(path, "actions")
        if not os.path.exists(actions_path):
            os.mkdir(actions_path)

        actionsTemp = ""
        actionsModelTemp = ""
        actionsModelTemp += modelHeader
        actionsModelTemp += typesTemp
        actionsModelTemp += connTemp

        init_list = []

        for title, data in actions.items():

            # models
            inp = data.get("input")
            outp = data.get("output")

            actionsName = tools.getModelName(title, "Action")
            inpClassName = tools.getModelName(title, "Input")
            outpClassName = tools.getModelName(title, "Output")

            actions_class_list.append(actionsName)
            init_list.append([title, actionsName])

            inp_data = {
                "className": inpClassName,
                "args": tools.ymlTransPy(inp)
            }
            outp_data = {
                "className": outpClassName,
                "args": tools.ymlTransPy(outp)
            }

            inpTemp = tools.renderStrTemplate(inp_data, MODEL_INFO)
            outpTemp = tools.renderStrTemplate(outp_data, MODEL_INFO)

            # model主要内容
            actionsModelTemp += inpTemp
            actionsModelTemp += outpTemp
            actionsModelTemp += BASERUNPARAM

            # action
            actionData = {
                "actionsName": actionsName,
                "name": title,
                "inputModel": inpClassName,
                "outputModel": outpClassName,
                "baseRunModel": "BASE_RUN_PARAM",
                "adapMdl": tools.getModelName("adapter"),
            }
            actionsTemp = tools.renderStrTemplate(actionData, ACTION_INFO)

            file_path = os.path.join(actions_path, f"{title}.py")
            if not os.path.exists(file_path):
                tools.writeFile(actionsTemp, file_path)
                logging.info(f"mkdir actions/{title}.py ok")

            # 生成测试文件
            file_path = os.path.join(tests_path, f"{title}.json")
            testData = tools.renderStrTemplate({"title": title},
                                               ACTION_FAST_API_INFO)
            tools.writeFile(testData, file_path)
            logging.info(f"mkdir tests/{title}.json ok")

        # 生成__init__.py
        file_path = os.path.join(actions_path, "__init__.py")
        initData = tools.renderStrTemplate({"init_list": init_list},
                                           INIT_INFO)
        tools.writeFile(initData, file_path)
        logging.info(f"mkdir actions/__init__.py ok")

        file_path = os.path.join(actions_path, "models.py")
        tools.writeFile(actionsModelTemp, file_path)
        logging.info(f"mkdir actions/models.py ok")
        # 生成actions的REST 测试接口
        file_path = os.path.join(path, "testAPI.py")
        testAPIData = tools.renderStrTemplate({"init_list": init_list},
                                              FAST_API_INFO)
        tools.writeFile(testAPIData, file_path)
        logging.info(f"mkdir testAPI.py ok")

        #===
    #===

    # 生成triggers
    triggers = yaml_data.get("triggers")
    if triggers:
        triggers_path = os.path.join(path, "triggers")
        if not os.path.exists(triggers_path):
            os.mkdir(triggers_path)

        triggersTemp = ""
        triggersModelTemp = ""
        triggersModelTemp += modelHeader
        triggersModelTemp += typesTemp
        triggersModelTemp += connTemp

        init_list = []

        for title, data in triggers.items():

            # models
            inp = data.get("input")
            outp = data.get("output")

            triggersName = tools.getModelName(title, "Trigger")
            inpClassName = tools.getModelName(title, "Input")
            outpClassName = tools.getModelName(title, "Output")

            triggers_class_list.append(triggersName)
            init_list.append([title, triggersName])

            inp_data = {
                "className": inpClassName,
                "args": tools.ymlTransPy(inp)
            }
            outp_data = {
                "className": outpClassName,
                "args": tools.ymlTransPy(outp)
            }

            inpTemp = tools.renderStrTemplate(inp_data, MODEL_INFO)
            outpTemp = tools.renderStrTemplate(outp_data, MODEL_INFO)

            # model主要内容
            triggersModelTemp += inpTemp
            triggersModelTemp += outpTemp

            # trigger
            triggerData = {
                "triggersName": triggersName,
                "name": title,
                "inputModel": inpClassName,
                "outputModel": outpClassName,
                "adapMdl": tools.getModelName("adapter"),
            }
            triggersTemp = tools.renderStrTemplate(triggerData,
                                                   TRIGGER_INFO)

            file_path = os.path.join(triggers_path, f"{title}.py")
            if not os.path.exists(file_path):
                tools.writeFile(triggersTemp, file_path)
                logging.info(f"mkdir triggers/{title}.py ok")

            # 生成测试文件
            file_path = os.path.join(tests_path, f"{title}.json")
            testData = tools.renderStrTemplate({"title": title},
                                               TRIGGER_FAST_API_INFO)
            tools.writeFile(testData, file_path)
            logging.info(f"mkdir tests/{title}.json ok")

        # 生成__init__.py
        file_path = os.path.join(triggers_path, "__init__.py")
        initData = tools.renderStrTemplate({"init_list": init_list},
                                           INIT_INFO)
        tools.writeFile(initData, file_path)
        logging.info(f"mkdir triggers/__init__.py ok")

        file_path = os.path.join(triggers_path, "models.py")
        tools.writeFile(triggersModelTemp, file_path)
        logging.info(f"mkdir triggers/models.py ok")

    #===

    # 创建入口文件　main.py
    mainData = {
        "pluginName": tools.getModelName(plugin_name,
                                         "Plugin").replace(" ", "_"),
        "actionClassees": actions_class_list,
        "triggerClassees": triggers_class_list
    }
    file_path = os.path.join(path, "main.py")
    mainTemp = tools.renderStrTemplate(mainData, MAIN_INFO)
    tools.writeFile(mainTemp, file_path)
    logging.info(f"mkdir main.py ok")

    # 生成util
    util_path = os.path.join(path, "util")
    if not os.path.exists(util_path):
        os.mkdir(util_path)
        logging.info("mkdir util ok")

    logging.info("^_^!! TemplateSourceCode done ")


def run(path: str, tests: str):

    main_path = os.path.join(path, "main.py")
    tests_path = os.path.join(path, tests)

    if not os.path.exists(tests_path):
        logging.error(f"请正确输入路径：{tests_path}")

    cmd = f"python {main_path} run < {tests_path}"
    os.system(cmd)


def http(path: str):
    main_path = os.path.join(path, "main.py")

    cmd = f"python {main_path} http"
    os.system(cmd)


