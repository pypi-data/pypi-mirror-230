# coding: utf-8
import logging
import os
import uuid
from concurrent import futures

import grpc

from taichu_serve.grpc_predict_v2_pb2_grpc import add_GRPCInferenceServiceServicer_to_server
from taichu_serve.app import app, init_model_service_instance
from taichu_serve.grpc_server import GrpcModelService, GrpcServerInterceptor
from taichu_serve.settings import parse_args
from taichu_serve.dockerfile import Dockerfile_template, launch_sh_template, \
    launch_sh_deploy_template, Dockerfile_deploy_template
from taichu_serve.third.tracer import init_opentelemetry

logger = logging.getLogger(__name__)


def init_project(name="project"):
    # 在当前目录下创建项目目录
    if not os.path.exists(name):
        os.mkdir(name)

    # 获取当前目录
    current_path = os.path.abspath(os.path.dirname(__file__))
    # 获取模板目录
    template_path = os.path.join(current_path, "template")
    # 拷贝模板目录下的文件到项目目录
    for file in os.listdir(template_path):
        if file == "__pycache__":
            continue
        if file.endswith("__init__.py"):
            continue

        if os.path.isdir(os.path.join(template_path, file)):
            if not os.path.exists(os.path.join(name, file)):
                os.mkdir(os.path.join(name, file))
            for sub_file in os.listdir(os.path.join(template_path, file)):
                if sub_file == "__pycache__":
                    continue
                if sub_file.endswith("__init__.py"):
                    continue
                with open(os.path.join(template_path, file, sub_file), "r") as f:
                    content = f.read()
                print("create file: ", os.path.join(name, file, sub_file))
                with open(os.path.join(name, file, sub_file), "w") as f:
                    f.write(content)
            continue

        with open(os.path.join(template_path, file), "r") as f:
            content = f.read()
        print("create file: ", os.path.join(name, file))
        with open(os.path.join(name, file), "w") as f:
            f.write(content)

    with open(os.path.join(name, "dependencies.txt"), "w") as f:
        f.write("# 请在这里添加apt-get安装的依赖，每行一个依赖，如：curl")
    print("create file: ", os.path.join(name, "dependencies.txt"))
    print("init project done!")


def deploy(name, base_image):
    if name is None or name == "":
        name = "taichu-serve-env"

    if base_image is None or base_image == "":
        base_image = "swr.cn-central-221.ovaijisuan.com/wair/taichu-serve:latest"
    if os.path.exists("Dockerfile"):
        print("Dockerfile已存在，请删除后重试！")
        return

    if os.path.exists("launch.sh"):
        os.remove("launch.sh")

    if not os.path.exists("requirements.txt"):
        with open("requirements.txt", "w") as f:
            f.write("taichu-serve")
        print("create file: ", "requirements.txt")

    if not os.path.exists("dependencies.txt"):
        with open("dependencies.txt", "w") as f:
            f.write("# 请在这里添加apt-get安装的依赖，每行一个依赖，如：curl")
        print("create file: ", "dependencies.txt")

        # 逐行读取dependencies.txt
    with open("dependencies.txt", "r") as f:
        dependencies = f.readlines()
        dependencies = [x.strip() for x in dependencies]
        # 跳过注释行
        dependencies = [x for x in dependencies if not x.startswith("#")]
        dependencies = [x for x in dependencies if x != ""]

    apt_install = ''
    for dependency in dependencies:
        if not dependency.startswith("RUN apt-get install -y"):
            apt_install = 'RUN  apt-get update && apt-get install -y '
        apt_install += dependency + " "
    dockerfile_content = Dockerfile_deploy_template.format(base_image=base_image, apt_install=apt_install)

    with open("launch.sh", "w") as f:
        f.write(launch_sh_deploy_template)
    print("create file: ", "launch.sh")
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    print("create file: ", "Dockerfile")

    print("build docker image...")
    tag = uuid.uuid4().hex[:8]
    image_name = f"{name}:{tag}"
    cmd = f"docker build -t {image_name} ."
    print(f"[CMD] {cmd} ")
    ret = os.system(cmd)
    if ret != 0:
        print("build docker image failed!")
        return

    print("build docker image done!")

    print("进入镜像调试命令：")
    print(f"[CMD] docker run -it -p 8080:8080 -p 8081:8081 -v $PWD:/home {image_name} bash")
    print("调试完成后，可以使用以下命令将镜像推送到仓库：")

    print("[CMD] docker tag {image_name} swr.cn-central-221.ovaijisuan.com/wair/{image_name}".format(
        image_name=image_name))
    print("[CMD] docker push swr.cn-central-221.ovaijisuan.com/wair/{image_name}".format(image_name=image_name))


def build_env(name, base_image):
    # 检查镜像名称是否合法
    if name is None or name == "":
        name = "taichu-serve-env"

    if base_image is None or base_image == "":
        base_image = "swr.cn-central-221.ovaijisuan.com/wair/taichu-serve:latest"
    if os.path.exists("Dockerfile"):
        print("Dockerfile已存在，请删除后重试！")
        return

    if os.path.exists("launch.sh"):
        os.remove("launch.sh")

    if not os.path.exists("requirements.txt"):
        with open("requirements.txt", "w") as f:
            f.write("taichu-serve")
        print("create file: ", "requirements.txt")

    if not os.path.exists("dependencies.txt"):
        with open("dependencies.txt", "w") as f:
            f.write("# 请在这里添加apt-get安装的依赖，每行一个依赖，如：curl")
        print("create file: ", "dependencies.txt")

    # 逐行读取dependencies.txt
    with open("dependencies.txt", "r") as f:
        dependencies = f.readlines()
        dependencies = [x.strip() for x in dependencies]
        # 跳过注释行
        dependencies = [x for x in dependencies if not x.startswith("#")]
        dependencies = [x for x in dependencies if x != ""]

    apt_install = ''
    for dependency in dependencies:
        if not dependency.startswith("RUN apt-get install -y"):
            apt_install = 'RUN  apt-get update && apt-get install -y '
        apt_install += dependency + " "
    dockerfile_content = Dockerfile_template.format(base_image=base_image, apt_install=apt_install)

    with open("launch.sh", "w") as f:
        f.write(launch_sh_template)
    print("create file: ", "launch.sh")
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    print("create file: ", "Dockerfile")

    print("build docker image...")
    tag = uuid.uuid4().hex[:8]
    image_name = f"{name}:{tag}"
    cmd = f"docker build -t {image_name} ."
    print(f"[CMD] {cmd} ")
    os.system(cmd)
    print("build docker image done!")

    print("进入镜像调试命令：")
    print(f"[CMD] docker run -it -p 8080:8080 -p 8081:8081 -v $PWD:/home {image_name} bash")
    print("调试完成后，可以使用以下命令将镜像推送到仓库：")

    print("[CMD] docker tag {image_name} swr.cn-central-221.ovaijisuan.com/wair/{image_name}".format(
        image_name=image_name))
    print("[CMD] docker push swr.cn-central-221.ovaijisuan.com/wair/{image_name}".format(image_name=image_name))


def cli(*args, **kwargs):
    args = parse_args()
    if args.action == "init":
        init_project()
        return
    if args.action == "build":
        build_env(args.name, args.from_image)
        return
    if args.action == "deploy":
        deploy(args.name, args.from_image)
        return

    args.http_port = kwargs.get("http_port", args.http_port)
    args.grpc_port = kwargs.get("grpc_port", args.grpc_port)

    # 初始化 opentelemetry
    init_opentelemetry(jaeger_url=args.jaeger_url, app=app)

    # 检查model_service是否存在
    if not os.path.exists(os.path.join(args.model_path, args.service_file)):
        logger.error(f"{args.service_file}不存在，请检查model_path是否正确！")
        return

    init_model_service_instance()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=args.max_concurrent_requests),
                         maximum_concurrent_rpcs=args.max_concurrent_requests + 5,
                         interceptors=[GrpcServerInterceptor()],
                         options=[("grpc.max_send_message_length", 50 * 1024 * 1024),
                                  ("grpc.max_receive_message_length", 50 * 1024 * 1024), ])

    add_GRPCInferenceServiceServicer_to_server(GrpcModelService(), server)
    server.add_insecure_port(f'[::]:{args.grpc_port}')

    server.start()
    logger.info("grpc server start at port %s", args.grpc_port)

    if args.grpc_only:
        server.wait_for_termination()

    app.run("0.0.0.0", args.http_port)
    return app
