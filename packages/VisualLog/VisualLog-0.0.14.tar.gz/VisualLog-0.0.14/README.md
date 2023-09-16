# README

可视化log分析工具，解决常用的log数据可视化需求

# docs

NO.  |文件名称|摘要
:---:|:--|:--
0004 | [ShellCmd](docs/0004_ShellCmd.md) | 获取shell命令数据
0003 | [SameLines](docs/0003_SameLines.md) | 比较两个文本数组
0002 | [MatplotlibZoom](docs/0002_MatplotlibZoom.md) | Matplotlib绘制可缩放、平移可视化数据
0001 | [LogParser](docs/0001_LogParser.md) | Kernel、Logcat、文本数据提取

# 发行PyPi处理流程

* pip3 install twine
* https://pypi.org/
  * 注册帐号
* python3 setup.py sdist bdist_wheel
* twine upload dist/*
  ```
  Uploading distributions to https://upload.pypi.org/legacy/
  Enter your username: zengjf
  Enter your password:
  Uploading VisualLog-0.0.0-py3-none-any.whl
  100% ---------------------------------------- 8.4/8.4 kB • 00:00 • ?
  Uploading VisualLog-0.0.0.tar.gz
  100% ---------------------------------------- 6.6/6.6 kB • 00:00 • ?
  
  View at:
  https://pypi.org/project/VisualLog/0.0.0/
  ```
