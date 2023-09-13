# Yantu-Tools For Python
Yantu-Tools-Python是言图科技提供的以Python语言编写的应用程序库，以实现对Yantu API便捷访问。它包括一个用于初始化的API资源的预定义类集，可以方便地访问Yantu API，以高效地使用言图私域知识库、言图文档问答等功能。

## 安装
pip安装
```
pip install --upgrade yantu-tools-python
```
或使用以下命令从源代码安装：
```
python setup.py install
```
## 主要功能
* 简单高效，用户只需配置专属密钥即可使用yantu API
* 高度定制化和数据安全的私域知识库
* 言图智能业务机器人
* 基于私域知识库的文档问答

## 用法
该库需要使用您帐户的密钥进行配置，该密钥可在[言图科技官方网站](http://www.yantu-tech.com/)上找到。  
### 资源初始化
```python
import yantu

yt_object = yantu.YantuObject("您的密钥")
```
### 私域知识库
```python
# 获取私域知识库中的文档列表
yt_object.get_doc_list()

# 上传文档到私域知识库
yt_object.upload_doc("您的文档路径")

# 删除私域知识库中文档
yt_object.delete_doc("您的文档名称")
```

### 