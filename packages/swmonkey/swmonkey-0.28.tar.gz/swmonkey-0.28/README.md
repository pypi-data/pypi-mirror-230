# 基于 pyautogui 的 Monkey 测试工具

## 运行

1. 进入 venv 环境

```
source venv/bin/activate
```

2. 安装依赖

```
pip install -r requirements.txt
```

3. 本地安装

```
pip install -e .
```

4. 执行命令

```
swmonkey -d 60 # 运行60秒
```

## 安装

```
pip install --index-url https://pypi.org/project swmonkey --upgrade
```

## 使用

### swmonkey

```
swmonkey -d 20 # 运行20秒
```

-d / --duration 指定运行时间

```
swmonkey -d 20 -r -p  ~/.swmonkey/20230911114348/actions.json # 回放 ~/.swmonkey/20230911114348/actions.json的数据
```

-r 以回放模式运行，需要搭配`-p` 参数指定回访数据的路径

-p 指定回放数据的路径

回放数据和日志的路径默认在 `~/.swmonkey/`下, 可以通过 `-p`参数指定

```
swmonkey # 远程shell运行,需要DISPLAY环境变量
```

### swmonkey_runner

`swmonkey_runner`是一个辅助命令，以进程分离的形式运行`swmonkey`, 目的是在 swmonkey 进程挂掉的时候，可以自动重启

```
swmonkey_runner -d 7200
```

```
swmonkey_runner -d 600000 --restart-x11 --password 123456
```


--restart-x11
开启这个参数，会在 swmonkey 挂掉的时候，自动重启 X11 服务，前提是终端需要配置了自动运行monkey, 如何配置参见:https://kb.cvte.com/pages/viewpage.action?pageId=377734914

--password
指定sudo密码，用于 swmonkey 进程挂掉的时候，自动重启 X11 服务

## 设计文档

https://kb.cvte.com/pages/viewpage.action?pageId=372571592

## 构建和发布

```
./auto-upload.sh
```

## 本地测试

```
python -m venv venv

source venv/bin/activate

pip install -e . # Install package in editable mode

swmonkey -d 15 # Run 15 seconds
# 查看日志文件, 日志文件和录制文件都在 ~/.swmonkey/ 目录下，目录名为时间戳
ls ~/.swmonkey/
```
