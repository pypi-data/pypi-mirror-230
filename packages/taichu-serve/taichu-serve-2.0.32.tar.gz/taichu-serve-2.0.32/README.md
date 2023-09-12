## 介绍

`taichu-serve` 是一个基于python的服务端模型部署框架，旨在提供一个简单易用的模型部署方案，让开发者可以专注于模型的开发和优化，而不用关心模型的部署和运维。

## 特性

-   **简单易用**：极简情况下，只需编写一个model_service.py文件，即可完成模型的部署。
-   **免写WebServer**：开发者无需编写Web服务，只需编写模型前后处理逻辑。
-   **多协议支持**：支持http、grpc、流式grpc三种协议。
-   **服务治理**：支持链路追踪、限流、探活等服务治理功能。
-   **性能指标**：内置了核心指标埋点，如QPS、延迟、吞吐量等。


## Quick Start

### 环境要求
-   Python 3.6+

### 1. 安装

```bash
pip3 install taichu-serve -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 初始化模型包
`taichu-serve`提供一个脚手架工具，可以帮助开发者快速初始化一个模型包。
```bash
taichu_serve init
```
执行后会在当前目录下生成一个名为`project`的文件夹，各个文件的介绍参考[模型包目录结构说明](#模型包目录结构说明)。
### 3. 编写模型服务代码
开发者需要修改模型包内的`model_service.py`文件内实现模型的前后处理逻辑，以及模型的加载、预热等逻辑。
参考[模型服务代码说明](#模型服务代码说明)。
### 4. 启动模型服务
开发者能够在本地启动模型服务，方便调试。
```bash
cd project
taichu_serve run
```
模型会在本地启动启动http服务和grpc服务，端口分别为`8080`和`8081`，可以通过[标准预测协议](https://github.com/kserve/kserve/tree/master/docs/predict-api/v2)进行预测请求。

### 5. 测试预测请求
脚手架预置了http、grpc、流式grpc三种测试脚本，开发者可以根据自己的需求修改测试脚本
```bash
# 测试http请求
python3 test/http_client.py
# 测试grpc请求
python3 test/grpc_client.py
# 测试流式请求
python3 test/stream_grpc_client.py
```

### [可选] 配置pip依赖和apt依赖
若taichu平台提供的基础环境镜像里缺少你的模型所需的依赖，你可以在模型包内添加`requirements.txt`和`dependencies.txt`文件，分别用于指定pip依赖和apt依赖。
模型服务启动时会自动安装这些依赖。

### [可选] 构建自定义运行环境镜像
>环境依赖：`Docker`
> 
>单独的模型包是不能被部署成服务的，模型包只有搭配一个镜像才能被部署成服务，镜像为模型包提供运行环境支撑。

如果taichu平台提供的基础镜像不能满足你的需求，通过配置pip依赖和apt依赖也无法解决你的问题。
开发者可以自己构建一个运行镜像，然后将镜像上传到平台swr仓库，再在平台上指定该镜像作为运行环境进行部署。
```bash
taichu_serve build --from_image {你的运行镜像} 
# 例如 taichu_serve build --from_image python:3.7
```
`taichu_serve build`能够将你的运行镜像改造成一个可在平台上部署的镜像，改造过程中会将模型包内的pip依赖和apt依赖安装到镜像内。
命令成功后会在本地生成一个可在平台部署的新镜像,镜像名关注命令行输出的`Successfully built`后的镜像名

`taichu_serve build`能改造你的基础镜像，使其能够用于在平台上部署。

#### 上传镜像到平台
本地测试完毕后，将镜像上传到平台swr仓库
```bash
docker tag {镜像名} {平台仓库地址}/{镜像名}
docker push {平台仓库地址}/{镜像名}
```
## 一键打包成自定义镜像
>环境依赖：`Docker`

taichu_serve提供了`deploy`命令，能够将模型包一键打包成一个可在平台上直接部署的自定义镜像。
```bash
taichu_serve deploy --from_image {你的运行镜像} 
```
`taichu_serve deploy`会将模型包完整拷贝到镜像内，还会将模型包内的pip依赖和apt依赖也安装到镜像内（非镜像启动时安装）。打包后生成的镜像具备完整的模型代码和运行环境，能够直接在通过自定义镜像方式导入平台后部署。
## 模型包目录结构说明
执行`taichu_serve init`后，会在当前目录下生成一个名为`project`的文件夹，目录结构如下：
```bash
project
├── test                            # 可选，测试脚本文件夹
│       ├── grpc_client.py          # 可选，grpc测试客户端
│       ├── http_client.py          # 可选，http测试客户端
│       └── stream_grpc_client.py   # 可选，流式grpc测试客户端
├── model_service.py                # 必填，模型服务自定义逻辑
├── models                          # 可选，模型文件夹
├── config.ini                      # 可选，模型服务配置文件
├── requirements.txt                # 可选，项目pip依赖
├── dependencies.txt                # 可选，项目apt依赖
├── launch.sh                       # 可选，镜像启动脚本。如果执行了taichu_serve build，会生成该文件，除非有特殊需求，否则不需要修改该文件
└── Dockerfile                      # 可选，镜像dockerfile。如果执行了taichu_serve build，会生成该文件，如有特殊需求，请基于该文件自行构建部署镜像
```

## 模型服务代码说明 
模型包内只有一个必填文件`model_service.py`，该文件内包含了模型服务的自定义逻辑，开发者需要在该文件内实现模型的前后处理逻辑，以及模型的加载、预热等逻辑。

### model_service.py
```python
import logging

from taichu_serve import ModelServer

logger = logging.getLogger(__name__)


class ModelService(ModelServer):
    def __init__(self, model_path):
        """
        Args:
            model_path: 模型文件夹路径
        """
        super(ModelService, self).__init__(model_path)
        logger.info("self.model_path: %s",
                    model_path)

    def _preprocess(self, input_data, context):
        """
        Args:
            input_data: 输入数据
            context: 请求上下文,一般用于流式请求
        """   
        logger.info('enter _preprocess')
        return input_data

    def _inference(self, preprocessed_result, context):
        logger.info('enter _inference')        
        return preprocessed_result

    def _postprocess(self, inference_result, context):
        logger.info('enter _postprocess')

        return inference_result
    
    # 可选，模型预热逻辑
    def _warmup(self):
        logger.info('warmup finished')
```

## 模型服务配置
模型服务配置文件`config.ini`，用于配置模型服务的运行参数，如模型服务的http端口、grpc端口、限流、worker数量等。
```ini
[rate-limiter] # 限流配置
# 最大并发数
max_concurrent_requests = 2

[server] # 模型服务配置
# grpc端口
grpc_port = 8080
# http端口
http_port = 8081 
# 是否只开启http服务
grpc_only = False
# worker数量
instances_num = 1 
```

## 示例项目 Examples

- 最小项目-[minimal](https://gitee.com/wair-ac/taichu-serve/tree/master/examples/minimal)
- 图像分类-[inception](https://gitee.com/wair-ac/taichu-serve/tree/master/examples/inception)
- 对话模型-[ChatTaichu](https://gitee.com/wair-ac/taichu-serve/tree/master/examples/chat_taichu)
- 流式语音识别-[asr_wenet](https://gitee.com/wair-ac/taichu-serve/tree/master/examples/asr_wenet)
