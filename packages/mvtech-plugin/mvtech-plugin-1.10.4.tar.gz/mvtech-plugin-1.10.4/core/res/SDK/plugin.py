"""
插件定义 抽象类
"""


class Plugin(object):

    def __init__(self):

        # 插件的３个组件
        self.adapter = {}
        self.actions = {}
        self.triggers = {}

    def add_adapter(self, adapterp):
        self.adapter[adapterp.name] = adapterp

    def add_actions(self, action):
        self.actions[action.name] = action

    def add_triggers(self, trigger):
        self.triggers[trigger.name] = trigger
 