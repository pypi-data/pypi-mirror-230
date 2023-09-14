from setuptools import setup, find_packages
import core

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()



setup(
    # 应用名
    name = "mvtech-plugin",

    # 作者
    author = "sandy",

    # 作者邮箱
    author_email = "tong@mvtech.com.cn",

    # 描述
    description = "插件生成等功能...",

    # 版本号
    version = core.VERSION,

    # 安装 当前目录下有哪些包
    packages = find_packages(),

    # 配合 MANIFEST.ni文件上传静态资源
    include_package_data = True,

    # 东方通社区
    url = "https://www.mvtech.cn/market/introduction",

    # py版本
    python_requires = '>=3',

    # 依赖
    install_requires = [
        "argparse",
        "loguru",
        "jinja2",
        "pyyaml",
        "fastapi",
        "jsonpointer",
        "uvicorn",
        "requests",
    ],

    # 入口
    entry_points={
        "console_scripts": [
            "mvtech-plugin = core.main:cmdline"
        ]
    },

    # 项目的详细描述
    long_description = long_description,
    long_description_content_type = "text/markdown",

    # 许可证
    license = 'MIT',
)



