# Super IDE Core

## 用户指南

您安装 Super IDE VSCode插件时会自动安装 Super IDE Core，这里简单介绍一下手动安装 Super IDE Core。

- pip 安装 Super IDE Core

```
$ python3 -m pip install -U super-ide
```

- 推荐使用get-superide.py脚本安装 Super IDE Core，因为这种方式和Super IDE VSCode插件采用了相同的方法。

```
$ git clone https://gitee.com/SuperIDE/super-ide.git 
$ cd super-ide/
$ python3 scripts/get-superide.py
```

### Run

您使用 Super IDE VSCode插件时内部会调用 Super IDE Core，这里简单介绍一下单独命令行方式使用 Super IDE Core：使用`super-ide`或`si`命令

```bash
super-ide --version
si --version
```

* [Super IDE Core Commands Guide](doc/CommandsGuide.md)

## 开发者指南

### 环境

Windows系统下使用[WSL](https://learn.microsoft.com/zh-cn/windows/wsl/)，Mac和Linux下可以直接运行在终端。推荐使用Conda环境。

本教程以WSL下Ubuntu系统的MiniConda环境安装使用为例。

#### WSL安装

如果没有**WSL**首先在Windows下安装[WSL下的Ubuntu](https://learn.microsoft.com/zh-cn/windows/wsl/install)。

#### Miniconda安装

下载[Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)到Ubuntu，在此目录下运行：

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

安装成功后刷新环境变量：

```bash
source .bashrc
```
执行完source .bashrc 之后，命令行提示信息前面就会有一个(base)，代表激活了base(最基础)环境。

```bash
conda deactivate		        #退出base环境
```

[参考](https://blog.51cto.com/u_13389043/6223883)

#### 准备Conda环境

创建side环境，后续在此环境下进行开发：

```bash
conda create --name side python=3	#创建名为side,python为最新3.x版本的环境
conda activate side		        #进入该环境
conda deactivate		        #退出该环境
```

### Install

下载本项目并进入项目目录：

```bash
git clone https://gitee.com/SuperIDE/super-ide.git 
cd super-ide/
```

- 源代码中开发者模式安装 Super IDE Core

  ```bash
  pip install -e .
  ```

  - `pip`会根据`setup.py`文件中的配置要求安装项目所需的依赖项，该选项将把项目安装在本目录下并在Python的site-packages目录中创建符号链接。


- 源代码中安装 Super IDE Core

  ```bash
  pip install .
  ```

  - `pip`会根据`setup.py`文件中的配置要求安装项目所需的依赖项，并将项目安装到Python的site-packages目录中。

​	验证安装：在命令行中输入`si`或`super-ide`，将看到帮助提示。

### Build

```
$ pip show setuptools
$ make pack
```

### Publish

```
$ make publish
```

运行命令之前需要将用户根目录下配置好 pypi 的 API Token。
格式如下：

```
[distutils]
index-servers =
    pypi
[pypi]
username = __token__
password = {api token}
```



## Super IDE Core Inside

- [make pack](doc/makepack.md)

## License

Copyright (c) 2022-present Mengning <contact@mengning.com.cn>

The Super IDE is licensed under the AGPL 3.0 license or commercial license.
