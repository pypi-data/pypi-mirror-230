# Flask settings
import argparse
import configparser
import logging
import os

DEFAULT_FROM_IMAGE = 'swr.cn-central-221.ovaijisuan.com/wair/taichu-serve:latest'
DEFAULT_IMAGE_NAME = 'taichu-serve-env'
DEFAULT_GRPC_PORT = 8080
DEFAULT_HTTP_PORT = 8081
DEFAULT_WORKERS = 1
DEFAULT_MODEL_PATH = './'
DEFAULT_SERVICE_FILE = 'model_service.py'
DEFAULT_MAX_CONCURRENT_REQUESTS = 100
DEFAULT_INSTANCES_NUM = 1
DEFAULT_ENV = 'dev'
DEFAULT_JAEGER_URL = "http://127.0.0.1:4317"

logger = logging.getLogger(__name__)


def parse_args():
    # 判断是否为命令行taichu_serve命令
    import sys
    if sys.argv[0].endswith('taichu_serve'):
        args = parse_args_from_cmd()
    else:
        args = argparse.Namespace()
        args.action = 'run'
        args.env = DEFAULT_ENV
        args.from_image = DEFAULT_FROM_IMAGE
        args.name = DEFAULT_IMAGE_NAME
        args.grpc_port = DEFAULT_GRPC_PORT
        args.http_port = DEFAULT_HTTP_PORT
        args.grpc_only = False
        args.model_path = DEFAULT_MODEL_PATH
        args.service_file = DEFAULT_SERVICE_FILE
        args.max_concurrent_requests = DEFAULT_MAX_CONCURRENT_REQUESTS
        args.instances_num = DEFAULT_INSTANCES_NUM
        args.workers = DEFAULT_WORKERS
        args.jaeger_url = DEFAULT_JAEGER_URL

    # 读取配置文件
    if not os.path.exists('config.ini'):
        logger.info('config.ini not found, use default config')
        return args

    config = configparser.ConfigParser()
    config.read('config.ini')
    args.grpc_port = config.getint('server', 'grpc_port', fallback=args.grpc_port)
    args.http_port = config.getint('server', 'http_port', fallback=args.http_port)
    args.grpc_only = config.getboolean('server', 'grpc_only', fallback=args.grpc_only)
    args.instances_num = config.getint('server', 'instances_num', fallback=args.instances_num)

    args.max_concurrent_requests = config.getint('rate-limiter', 'max_concurrent_requests', fallback=1)

    return args


def parse_args_from_cmd():
    parser = argparse.ArgumentParser(description='Taichu Model Server')
    parser.add_argument('action', action="store", choices=['init', 'run', 'build', 'deploy'], default='run')

    parser.add_argument('--from_image', action="store",
                        default=DEFAULT_FROM_IMAGE, type=str)
    parser.add_argument('--name', action="store", default=DEFAULT_IMAGE_NAME, type=str)
    parser.add_argument('--env', action="store", default=DEFAULT_ENV, type=str)

    parser.add_argument('--grpc_port', action="store", default=DEFAULT_GRPC_PORT, type=int)
    parser.add_argument('--http_port', action="store", default=DEFAULT_HTTP_PORT, type=int)
    parser.add_argument('--grpc_only', action="store", default=False, type=bool)
    parser.add_argument('--model_path', action="store", default=DEFAULT_MODEL_PATH, type=str)
    parser.add_argument('--service_file', action="store", default=DEFAULT_SERVICE_FILE, type=str)
    parser.add_argument('--max_concurrent_requests', action="store", default=DEFAULT_MAX_CONCURRENT_REQUESTS, type=int)
    parser.add_argument('--instances_num', action="store", default=DEFAULT_INSTANCES_NUM, type=int)
    parser.add_argument('--jaeger_url', action="store", default=DEFAULT_JAEGER_URL, type=str)

    args, unknown = parser.parse_known_args()
    logger.warning('unknown args: %s', unknown)
    return args
