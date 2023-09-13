### mvtech_plugin

---

#### 简介

**mvtech_plugin**是MVTech插件脚手架

#### 基本架构结构

```txt
.
├── actions
│   ├── __init__.py
│   ├── ???.py     
│   ├── models.py
├── Dockerfile
├── help.md
├── icon.png
├── main.py
├── Makefile
├── plugin.yaml
├── requirements.txt
├── make_image.sh
├── SDK
│   ├── __init__.py
│   ├── base.py
│   ├── cli.py
│   ├── http_run.py
│   ├── models.py
│   ├── plugin.py
│   ├── run_define.py
│   └── web.py
├── testAPI.py
│   ├── ???.json
└── triggers
    └── models.py
    └── ???.py
```

- ?_plugin.yaml: 模板文件，定义插件．
- actions/???.py: 根据模板文件定义生成动作．
- triggers/???.py: 根据模板文件定义生成触发器．
- actions/models.py 和 triggers/models.py: 模板文件继承pydantic
- testAPI: FastAPI测试入口
- make_image.sh 打包脚本

#### 环境要求

- python3.+

#### 安装 依赖

pip install -r requirements.txt

### 脚手架离线自定义打包安装

#### 脚手架打包

    python .\setup.py sdist

#### 脚手架生成的压缩包解压后执行下面命令安装

    python setup.py install

#### 脚手架卸载

    pip uninstall mvtech-plugin  -y

#### 脚手架使用

    执行本地脚手架
    mvtech-plugin -h

```
usage: mvtech-plugin [-h] [-v] [-g GENERATE] [-r RUN] [-hp] [-t TEST] [-tb] [-mki]

插件生成器

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         查看版本
  -g GENERATE, --generate GENERATE
                        插件生成
  -r RUN, --run RUN     运行action
  -hp, --http           启动api接口
  -t TEST, --test TEST  测试
  -tb, --tarball        插件打包
  -mki, --mkimg         制作成docker镜像     
```  

### 打包出现#!/usr/bin/env python 
- vi 文件名
- : set ff = unix
- : wq

### 打docker镜像包 并且下载过程
make image
docker save mvtech/kafka:1.0.0 -o mvtech-kafka-1.0.0.tar

### 生成系统安装包
make tarball

#### 离线打Docker包

- docker save <myimage>:<tag> | gzip > <myimage>_<tag>.tar.gz

- docker save mvtech/rest:1.0.0 | gzip > mvtech_rest_1.0.0.tar.gz

#### 属性类型定义
* "string": "str",
* "bytes": "str",
*  "boolean": "bool",
*  "float": "float",
* "date": "str",
* "object": "dict",
* "password": "str",
* "integer": "int",
* "file": "dict"
