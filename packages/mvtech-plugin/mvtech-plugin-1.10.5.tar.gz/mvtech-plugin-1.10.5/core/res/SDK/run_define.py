try:
    from .base import log, checkModel, checkTriggerModel
except Exception:
    from base import log, checkModel, checkTriggerModel

import traceback
import requests
import asyncio

class Actions(object):

    def __init__(self):

        self._output = {"version": "v1", "type": "action_event", "body": {}}

        #   name 按规范应小写且用下划线隔开单词
        self.name = ""

        #   入参 校验类
        self.inputModel = None

        #   出参 校验类
        self.outputModel = None

        #   适配器 校验类
        self.adapMdl = None

    def adapter(self, data: dict):

        ...

    def run(self, params):

        ...

    def _test(self, adapter_data):
        """
        #   运行适配器
        参数说明：
        adapter_data:dict,    #   适配器数据
        """
        log("info", "运行适配器中")

        #   校验入参数据
        log("info", "校验适配器数据")

        try:
            checkModel(adapter_data, self.adapMdl)
            self.adapter(adapter_data)
            log("info", "适配器运行正常")
            log("info", "构建适配器运行信息")
            output = self._buildOutput({}, True)
            return output

        except Exception as error:
            log("error", f"适配器发生异常，错误原因：\n{error}")
            error_trace = traceback.format_exc()
            log("info", "构建适配器错误信息")
            output = self._buildOutput({}, False, error_trace)
            return output

    def _run(self, input_data: dict, adapter_data: dict):
        """
        #   运行全流程
        参数说明：
        input_data:dict,    #   入参数据
        adapter_data:dict,    #   适配器数据
        """
        log("info", "插件运行中")

        #   校验入参数据
        log("info", "校验入参数据")
        checkModel(input_data, self.inputModel)

        #   运行adapter
        output = self._test(adapter_data)

        #   适配器异常时直接返回错误输出
        if output["body"]["status"] == "False":
            return output

        #   运行run
        try:
            log("info", "执行功能中")
            log("info", f"入参数据为：\n  {input_data}")

            output_data = self.run(input_data)

            log("info", "功能执行完成")

        except Exception as error:
            #   收集错误信息
            log("error", error)
            error_trace = traceback.format_exc()
            log("error", f"详细错误信息：\n{error_trace}")
            #   构建错误输出的output
            log("info", "构建错误信息")
            output = self._buildOutput({}, False, error_trace)

        else:
            #   当运作正常时才需要做出参验证
            log("info", "校验出参数据")
            checkModel(output_data, self.outputModel)
            #   构建output
            log("info", "构建输出数据")
            output = self._buildOutput(output_data, True)

        return output
    def _run(self, input_data: dict, adapter_data: dict, baseRunModel: dict):
        """
        #   运行全流程
        参数说明：
        input_data:dict,    #   入参数据
        adapter_data:dict,    #   适配器数据
        """
        log("info", "插件运行中")

        #   校验入参数据
        log("info", "校验入参数据")
        checkModel(input_data, self.inputModel)

        #   运行adapter
        output = self._test(adapter_data)

        #   适配器异常时直接返回错误输出
        if output["body"]["status"] == "False":
            return output

        #   运行run
        try:
            log("info", "执行功能中")
            log("info", f"入参数据为：\n  {input_data}")
            input_data['baseRunModel'] = baseRunModel
            output_data = self.run(input_data)

            log("info", "功能执行完成")

        except Exception as error:
            #   收集错误信息
            log("error", error)
            error_trace = traceback.format_exc()
            log("error", f"详细错误信息：\n{error_trace}")
            #   构建错误输出的output
            log("info", "构建错误信息")
            output = self._buildOutput({}, False, error_trace)

        else:
            #   当运作正常时才需要做出参验证
            log("info", "校验出参数据")
            checkModel(output_data, self.outputModel)
            #   构建output
            log("info", "构建输出数据")
            output = self._buildOutput(output_data, True)

        return output
    
    def _buildOutput(self,
                     output_data: dict = {},
                     status: bool = True,
                     error_trace: str = ""):
        """
        #   构建出参信息，包括日志信息
        参数说明：
        output_data:dict,   #   输出信息
        status:bool,    #   run执行状态，执行成功为True，不成功为False
        error_trace:str,  #   详细的错误信息，用于给开发人员看
        """

        try:
            from .base import log_data
        except Exception:
            from base import log_data

        output = self._output

        output["body"]["output"] = output_data

        output["body"]["status"] = str(status)
        output["body"]["log"] = log_data
        output["body"]["error_trace"] = error_trace

        print(output)

        return output

    def _popEmpty(self, params):
        """
        #   采用深度遍历算法剔除载荷中的所有空参数，注意是所有！！！
        #   空参数包括："",{},None,[]
        参数说明：
        params:dict/list,   #   需要剔除空参数的字典或列表

        返回剔除完毕的字典或列表
        """
        params_temp = params.copy()
        if type(params) == dict:
            for key in params:
                if type(params[key]) == dict:
                    params_temp[key] = self._popEmpty(params_temp[key])
                if type(params[key]) == list:
                    params_temp[key] = self._popEmpty(params_temp[key])
                if params_temp[key] in ["", {}, None, []]:
                    params_temp.pop(key)
            return params_temp
        if type(params_temp) == list:
            for index in range(len(params_temp)):
                if params_temp[index] in ["", {}, None, []]:
                    params_temp.pop(index)
                    return self._popEmpty(params_temp)
                if type(params_temp[index]) in [list, dict]:
                    return self._popEmpty(params_temp[index])
        return params_temp


class Triggers(object):

    def __init__(self):

        self._output = {"version": "v1", "type": "trigger_event", "body": {}}

        #   name 按规范应小写且用下划线隔开单词
        self.name = ""

        #   发送到
        self.nextStep = None

        #   入参 校验类
        self.inputModel = None

        #   出参 校验类
        self.outputModel = None

        #   适配器 校验类
        self.adapMdl = None

    def adapter(self, data: dict):

        ...

    def run(self, params):

        ...

    def _test(self, adapter_data):
        """
        #   运行适配器
        参数说明：
        adapter_data:dict,    #   适配器数据
        """
        log("info", "运行适配器中")

        #   校验入参数据
        log("info", "校验适配器数据")

        try:
            checkModel(adapter_data, self.adapMdl)
            self.adapter(adapter_data)
            log("info", "适配器运作正常")
            log("info", "构建适配器运行信息")
            output = self._buildOutput({}, True)
            return output

        except Exception as error:
            log("error", f"适配器异常，错误原因：\n{error}")
            error_trace = traceback.format_exc()
            log("error", f"详细错误信息：\n{error_trace}")
            log("info", "构建适配器错误信息")
            output = self._buildOutput({}, False, error_trace)
            return output

    async def _run(self, input_data, adapter_data, next_step):
        """
        #   运行全流程
        参数说明：
        input_data:dict,    #   入参数据
        adapter_data:dict,    #   适配器数据
        next_step:dict,    #   下一步配置
        """
        log("info", "插件运行中")

        # self.dispatcher_url = dispatcher_url
        self.nextStep = next_step
        log("info", f"触发器回调数据 \n{self.nextStep}")
        #   校验入参数据
        log("info", "校验入参数据")
        checkTriggerModel(input_data, self.inputModel)

        #   运行adapter
        output = self._test(adapter_data)

        #   适配器异常时直接返回错误输出
        if output["body"]["status"] == "False":
            return output

        #   运行run
        try:
            log("info", "执行功能中")

            #   异步方式执行触发器，非阻塞
            asyncio.run(self.run(input_data))
            log("info", "触发器功能执行完成")

        except Exception as error:
            #   收集错误信息
            log("start_error", error)
            error_trace = traceback.format_exc()
            #   构建错误输出的output
            log("info", "构建错误信息")
            output = self._buildOutput({}, False, error_trace)

        else:
            output = self._buildOutput({}, True)
        return output

    def send(self, data: dict = {}):

        if self.nextStep is None:
            log("error", "没有配置下一步")
            return
        dis_url = self.nextStep.send_url
        if dis_url == "":
            log("error", "没有配置转发URL")
            return
        checkModel(data, self.outputModel)

        headers = {"Authorization":  self.nextStep.jwt}
        log("info", f"发送{dis_url} head:{headers} \n数据中")

        print(data)
        response = requests.post(dis_url, json=data, headers=headers, verify=False)

        log("info", f"发送完成，状态码：{response.status_code}\n返回信息：{response.text}")

        return response

    def _buildOutput(self,
                     output_data: dict = {},
                     status: bool = True,
                     error_trace: str = ""):
        """
        #   构建出参信息，包括日志信息
        参数说明：
        output_data:dict,   #   输出信息
        status:bool,    #   run执行状态，执行成功为True，不成功为False
        error_trace:str,  #   详细的错误信息，用于给开发人员追踪错误
        """

        try:
            from .base import log_data
        except Exception:
            from base import log_data

        output = self._output
        output["body"]["output"] = output_data

        output["body"]["status"] = str(status)
        output["body"]["log"] = log_data
        output["body"]["error_trace"] = error_trace

        print(output)

        return output

    def _popEmpty(self, params):
        """
        #   采用深度遍历算法剔除载荷中的所有空参数，注意是所有！！！
        #   空参数包括："",{},None,[]
        参数说明：
        params:dict/list,   #   需要剔除空参数的字典或列表

        返回剔除完毕的字典或列表
        """
        params_temp = params.copy()
        if type(params) == dict:
            for key in params:
                if type(params[key]) == dict:
                    params_temp[key] = self._popEmpty(params_temp[key])
                if type(params[key]) == list:
                    params_temp[key] = self._popEmpty(params_temp[key])
                if params_temp[key] in ["", {}, None, []]:
                    params_temp.pop(key)
            return params_temp
        if type(params_temp) == list:
            for index in range(len(params_temp)):
                if params_temp[index] in ["", {}, None, []]:
                    params_temp.pop(index)
                    return self._popEmpty(params_temp)
                if type(params_temp[index]) in [list, dict]:
                    return self._popEmpty(params_temp[index])
        return params_temp

