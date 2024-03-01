TODO : 介绍两款大模型的apikey的申请方式，阿里云oss bucket的申请

## code and result
model-test文件夹存储两个大模型的测试文件，通过API调用大模型进行测试
test-record文件夹存储测试记录，具体到每个类的每张图片的结果

## qwen-vl-plus

根据以下网页的教程，配置环境，下载dashscope

https://help.aliyun.com/zh/dashscope/developer-reference/install-dashscope-sdk

根据以下网页的教程，申请apikey

https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key


注册apikey后，在qwen的测试代码部分填写apikey信息
```python
dashscope.api_key = "YOUR_API_KEY"
```


## glm-4v

根据以下网页的教程，配置环境，下载zhipuai

https://open.bigmodel.cn/dev/api#overview

根据以下网页的教程，申请apikey

https://open.bigmodel.cn/usercenter/apikeys


注册apikey后，在glm的测试代码部分填写apikey信息
```python
client = ZhipuAI(api_key="YOUR_API_KEY")
```


## oss

由于glm-4v接收URL作为输入，需要将img临时上传得到公共URL，再输入给glm-4v

以下是临时上传的教程，在下面的网页中注册一个bucket

https://oss.console.aliyun.com/bucket

注册bucket后，在glm的测试代码部分填写相关信息
```python
# 自己的阿里云Access Key ID和Access Key Secret
auth = oss2.Auth('YOUR_KEY_ID', 'YOUR_KEY_SECRET')

# Bucket名称和数据中心所在的区域
bucket = oss2.Bucket(auth, 'http://oss-cn-guangzhou.aliyuncs.com', 'YOUR_BUCKET_NAME')
```

