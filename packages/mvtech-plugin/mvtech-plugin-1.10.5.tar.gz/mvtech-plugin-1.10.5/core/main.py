import os
import argparse

import core

from core.cli_methods import generate, run, http
"""
入口
"""


def cmdline():

    parser = argparse.ArgumentParser(description="插件生成器")

    parser.add_argument("-v", "--version", help="查看版本", action="store_true")
    parser.add_argument("-g", "--generate", help="插件生成", action="append")
    parser.add_argument("-r", "--run", help="执行动作", action="append")
    parser.add_argument("-hp", "--http", help="启动Http服务", action="store_true")

    args = parser.parse_args()

    if args.version:
        print(f"mvtech-plugin: {core.VERSION}")

    elif args.generate:

        yml = (args.generate)[0]

        generate(os.getcwd(), yml)

    elif args.run:

        path = os.getcwd()
        tests_path = args.run[0]

        run(path, tests_path)

    elif args.http:

        path = os.getcwd()

        http(path)
 

if __name__ == '__main__':
    cmdline()
