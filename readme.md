Laplace 是一个插件化实现的语音助手

# 下载
直接克隆当前仓库到您的项目之中
```shell
git clone https://github.com/AnthonySun256/Laplace.git
```

# 使用
将 Laplace 文件夹放到您的项目之中，并新建一个 Plugins 文件夹存放插件：具体可以参考 examples 文件夹
```python
from Laplace.laplace import Laplace
ll = Laplace()
ll.spin() # 开始事件轮询
```
