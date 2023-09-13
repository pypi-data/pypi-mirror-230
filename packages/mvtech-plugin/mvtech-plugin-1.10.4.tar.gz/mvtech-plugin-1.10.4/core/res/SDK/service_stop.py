
from threading import Timer
# import asyncio
import uvicorn
try:
    from .base import log
except Exception: 
    from base import log
import sys, os
# 服务是否有未运行完的action
is_action = True
live_count = 0
# action都运行结束后开始服务倒计时
dead_count = 60

timeFinish = False
def live_add():
    global live_count
    live_count = live_count + 1
    init_dead_count()

def live_sub():
    global live_count
    live_count = live_count - 1
    init_dead_count()
#  定时器每1秒执行一次,action执行速度快
def init_dead_count():
    global dead_count
    dead_count = 60


def do_check_end():
    global dead_count
    global live_count
    # 存活进程大于0说明有进程在运行
    if live_count > 0:
       log('info','正常运行数量:'+str(live_count))
       dead_count = 60
       return
    
    if dead_count > 0:
        log('info','倒计时：'+str(dead_count))
        dead_count = dead_count - 1
    else:
        global timeFinish
        timeFinish = True
        log('error','服务倒计时结束，停止服务')
        # sys.exit(0)        
        os._exit(0)
        # raise Exception("服务倒计时结束，停止服务")

class RepeatingTimer(Timer): 
    def run(self):
        # while not self.finished.is_set():
        while not timeFinish:
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)

def start_live(userver:uvicorn.Server):
    log('info',f'运行服务{userver}')
    # global userver1
    # userver1 = userver
    t = RepeatingTimer(1.0,do_check_end)
    t.start()
# start_live()