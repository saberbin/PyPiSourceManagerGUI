# PyPiSourceManagerGUI
主程序即`PyPiSourceManagerGUI`目录下的`PyPiSourceManagerGUI.py`文件。
直接运行即可启动程序。因为没有使用到第三方的包，所以可以直接启动。
运行
```shell
git clone https://github.com/saberbin/PyPiSourceManagerGUI.git
cd PyPiSourceManagerGUI
# 如果是Windows的cmd或者powershell7以下的终端可能是
chdir PyPiSourceManagerGUI
python PyPiSourceManagerGUI.py
```

# PIP源
```text
官方源：
https://pypi.org/simple

国内源：
阿里云：https://mirrors.aliyun.com/pypi/simple/ 
清华大学：https://pypi.tuna.tsinghua.edu.cn/simple/ 
中国科学技术大学：https://pypi.mirrors.ustc.edu.cn/simple/ 
豆瓣：http://pypi.douban.com/simple/ 
腾讯云：https://mirrors.cloud.tencent.com/pypi/simple 
华为云：https://repo.huaweicloud.com/repository/pypi/simple/ 
华中科技大学：http://pypi.hustunique.com/
网易：https://mirrors.163.com/pypi/simple/
```

# pip源修改方式
pip源的修改方式有两种：通过命令行修改，或者是修改pip.ini文件
这两种修改方式本质都是一样的——修改pip.ini文件。调用命令`pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple`修改pip源，本质上也是pip去修改pip.ini文件。

## 通过命令行修改pip源
永久换源命令：
```shell
# 清华源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# 阿里源
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
# 腾讯源
pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple
# 豆瓣源
pip config set global.index-url http://pypi.douban.com/simple/
# 换回默认源
pip config unset global.index-url
```
## 直接修改pip.ini
pip文件
```text
[global]
index-url = https://pypi.org/simple
```
修改的时候直接打开文件（使用文件编辑器即可打开），然后修改`index-url`的值即可
```text
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
```
然后保存关闭文件即可。

### 临时换源安装第三方库
可以使用`-i`参数临时修改源安装第三方库
```shell
pip install requests -i https://mirrors.aliyun.com/pypi/simple/
```

# 编译成Windows可执行文件
如果需要编译成Windows下的可执行文件，需要第三方库`pyinstaller`
```shell
# 安装pyinstaller
pip install pyinstaller
cd PyPiSourceManagerGUI  # chdir PyPiSourceManagerGUI
pyinstaller -F -w PyPiSourceManagerGUI.py
# 也可以附带其他参数或者是其他程序图标文件，这里以默认为主 
```
执行完成之后会在当前目录生产dist、build目录以及一个spec文件，exe文件在dist目录下面。
如果想要重新生成exe文件则需要删掉spec文件再执行一次命令即可。

# download
```text
https://github.com/saberbin/PyPiSourceManagerGUI/releases/tag/v1.0
```
[v1.0 PyPiSourceManagerGUI](https://github.com/saberbin/PyPiSourceManagerGUI/releases/tag/v1.0)



