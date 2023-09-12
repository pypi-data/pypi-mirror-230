

Dockerfile_template = """
FROM {base_image}


USER root

WORKDIR /opt
COPY ./launch.sh /opt/launch.sh
COPY ./requirements.txt /opt/requirements.txt

RUN apt-get update && apt-get install -y unzip vim
RUN chmod -R 777 /opt/launch.sh && chmod -R 777 /opt/requirements.txt
RUN chmod -R 777 /home

# 安装apt依赖
{apt_install}

RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --force-reinstall

WORKDIR /home

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["/opt/launch.sh"]

# 构建镜像命令： docker build -t taichu-serve-env .
# 运行镜像命令： docker run -it  -v $PWD:/home taichu-serve-env bash
# 推送镜像命令： 
#               docker tag taichu-serve-env swr.cn-central-221.ovaijisuan.com/wair/taichu-serve-env
#               docker push swr.cn-central-221.ovaijisuan.com/wair/taichu-serve-env
"""

launch_sh_template = """#!/bin/bash
# 请不要修改这个文件
# Do Not Modify This File
set -e

default_triton_grpc_port=8001
default_grpc_port=8080
default_http_port=8081
default_jaeger_url="http://clickhouse-streaming-collector.tracing:4317"

cp_and_unzip() {
    start_time=`date +%s`
    cp -rf $1 .
    end_time=`date +%s`
    echo "copy file time: $((end_time-start_time))s"
    
    set +e
    file_name=$(ls | grep .tar.gz)
    set -e
    if [ -n "$file_name" ]; then
        start_time=`date +%s`
        tar -zxvf $file_name -C $2
        end_time=`date +%s`
        echo "unzip file time: $((end_time-start_time))s"
        echo "clean file: $file_name"
        rm -rf $file_name
    fi
    
    set +e
    file_name=$(ls | grep .zip)
    set -e
    if [ -n "$file_name" ]; then
        start_time=`date +%s`
        unzip $file_name -d $2
        end_time=`date +%s`
        echo "unzip file time: $((end_time-start_time))s"
        echo "clean file: $file_name"
        rm -rf $file_name
    fi
    
    set +e
    file_name=$(ls | grep .tar)
    set -e
    if [ -n "$file_name" ]; then
        start_time=`date +%s`
        tar -xvf $file_name -C $2
        end_time=`date +%s`
        echo "unzip file time: $((end_time-start_time))s"
        echo "clean file: $file_name"
        rm -rf $file_name
    fi
}
    
    

if [ -z $triton_grpc_port ];then
    triton_grpc_port=$default_triton_grpc_port
fi
if [ -z $grpc_port ];then
    grpc_port=$default_grpc_port
fi
if [ -z $http_port ];then
    http_port=$default_http_port
fi

if [ -z $jaeger_url ];then
    jaeger_url=$default_jaeger_url
fi

if [ -z $INFER_CODE_PATH ];then
  echo "[FATAL] env INFER_CODE_PATH is not set"
  sleep 5
  exit 1
fi

# 生成临时的随机目录
random_dir=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1)
mkdir ~/$random_dir
echo "generate random dir: ~/$random_dir"
cd ~/$random_dir

# 如果INFER_CODE_PATH既不是文件也不是目录，则报错
if [ ! -d "$INFER_CODE_PATH" ] && [ ! -f "$INFER_CODE_PATH" ]; then
    echo "[FATAL] env INFER_CODE_PATH is not a file or dir"
    sleep 5
    exit 1
fi

if [ -d "$INFER_CODE_PATH" ]; then
    start_time=`date +%s`
    cp -rf $INFER_CODE_PATH/* .
    end_time=`date +%s`
    echo "copy model package dir time: $((end_time-start_time))s"
fi

# 如果INFER_CODE_PATH是文件，则解压
if [ -f "$INFER_CODE_PATH" ]; then
    mkdir -p unpack
    cp_and_unzip $INFER_CODE_PATH ./unpack
    cd unpack
    
    # 如果解压后只有一个文件夹，则进入文件夹
    set +e
    dir_num=$(ls -l | grep ^d | wc -l)
    file_num=$(ls | wc -l)
    set -e
    if [ $dir_num -eq 1 ]; then
        if [ $file_num -eq 1 ]; then
            cd $(ls -l | grep ^d | awk '{print $NF}')
        fi
    fi
fi

# 如果设置了MODEL_PATH，则拷贝模型文件
if [ -n "$MODEL_PATH" ]; then

    if [ ! -d "$MODEL_PATH" ] && [ ! -f "$MODEL_PATH" ]; then
        echo "[FATAL] env MODEL_PATH is not a file or dir"        
    fi
    
    if [ -d "$MODEL_PATH" ]; then
        start_time=`date +%s`
        cp -rf $MODEL_PATH/* ./models
        end_time=`date +%s`
        echo "copy model ckpt dir time: $((end_time-start_time))s"
    fi
    
    if [ -f "$MODEL_PATH" ]; then
        mkdir -p models
        cp_and_unzip $MODEL_PATH ./models
    fi
fi


# 检查是否存在models目录
if [ -d "models" ]; then
  echo "start tritonserver"
  # 启动tritonserver
  nohup tritonserver --model-repository=./models  --grpc-port=$triton_grpc_port  > tritonserver.log 2>&1 &

  # 等待tritonserver启动
  sleep 10
  cat tritonserver.log
fi

# 判断是否存在requirements.txt
if [ -f "requirements.txt" ]; then
  echo "install requirements.txt"
  pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

# 判断是否存在dependencies.txt
if [ -f "dependencies.txt" ]; then
  echo "install dependencies.txt"
  cat dependencies.txt | while read rows
  do
    # 跳过空行，去掉行首行尾的空格
    if [ -z "$rows" ]; then
      continue
    fi
    # 跳过注释行
    if [[ $rows =~ ^#.* ]]; then
      continue
    fi
    rows=`echo $rows | sed 's/^[ \t]*//g' | sed 's/[ \t]*$//g'`
    echo "install $rows"
    apt-get install -y $rows
  done
fi

taichu_serve run  --env prod --grpc_port $grpc_port --http_port $http_port --jaeger_url $jaeger_url
"""


Dockerfile_deploy_template = """
FROM {base_image}


USER root

WORKDIR /opt
COPY ./launch.sh /opt/launch.sh
COPY ./requirements.txt /opt/requirements.txt

RUN chmod -R 777 /opt/launch.sh && chmod -R 777 /opt/requirements.txt

# 安装apt依赖
{apt_install}

RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --force-reinstall

WORKDIR /home
RUN mkdir -p /home/project

WORKDIR /home/project
COPY . .
RUN chmod -R 777 /home

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["/opt/launch.sh"]

# 构建镜像命令： docker build -t taichu-serve-env .
# 运行镜像命令： docker run -it  -v $PWD:/home taichu-serve-env bash
# 推送镜像命令： 
#               docker tag taichu-serve-env swr.cn-central-221.ovaijisuan.com/wair/taichu-serve-env
#               docker push swr.cn-central-221.ovaijisuan.com/wair/taichu-serve-env
"""

launch_sh_deploy_template = """#!/bin/bash
# 请不要修改这个文件
# Do Not Modify This File
set -e

default_triton_grpc_port=8001
default_grpc_port=8080
default_http_port=8081
default_jaeger_url="http://clickhouse-streaming-collector.tracing:4317"


if [ -z $triton_grpc_port ];then
    triton_grpc_port=$default_triton_grpc_port
fi
if [ -z $grpc_port ];then
    grpc_port=$default_grpc_port
fi
if [ -z $http_port ];then
    http_port=$default_http_port
fi
if [ -z $jaeger_url ];then
    jaeger_url=$default_jaeger_url
fi

cd /home/project

# 检查是否存在models目录
if [ -d "models" ]; then
  echo "start tritonserver"
  set +e
  
  # 启动tritonserver
  nohup tritonserver --model-repository=./models  --grpc-port=$triton_grpc_port  > tritonserver.log 2>&1 &

  # 等待tritonserver启动
  sleep 10
  cat tritonserver.log
  
  set -e
fi

taichu_serve run  --env prod --grpc_port $grpc_port --http_port $http_port --jaeger_url $jaeger_url
"""