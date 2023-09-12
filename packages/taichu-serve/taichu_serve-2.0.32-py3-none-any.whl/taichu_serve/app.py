# -*- coding: utf-8 -*-
"""
DL webservice app
"""
import inspect
import json
import logging
import os
import sys
import threading
import time
import traceback
import typing
import pickle
import uuid
from opentelemetry import trace
from opentelemetry.trace import set_span_in_context

from flask import Flask, request, g

from taichu_serve.log import init_logger
from taichu_serve.settings import parse_args
from taichu_serve.ratelimiter import semaphore

args = parse_args()
if args.env == "prod":
    init_logger(json_format=True)
else:
    init_logger()

app = Flask("app")

from taichu_serve.error_code import ModelNotFoundError, ModelPredictError, TooManyRequestsError
from taichu_serve import ModelServer
from taichu_serve.common import Local
from taichu_serve.third import tracer


LOGGER = logging.getLogger(__name__)

import multiprocessing

workers_status = []


class WorkersPipeMgr(object):
    def __init__(self, num):
        self._list = []
        self._occupied = []
        self._lock = threading.Lock()
        self._num = num

    def append(self, pipe):
        with self._lock:
            self._list.append(pipe)
            self._occupied.append(False)

    def acquire(self, request_id):
        with self._lock:
            hash_value = hash(request_id)
            index = hash_value % self._num

            if not self._occupied[index]:
                self._occupied[index] = True
                return self._list[index]

            return None

    def release(self, request_id):
        with self._lock:
            hash_value = hash(request_id)
            index = hash_value % self._num

            if self._occupied[index]:
                self._occupied[index] = False


workers_pipe = WorkersPipeMgr(args.instances_num)


def worker_main_loop(args, pipe, status):
    # pwd = os.path.dirname(os.path.abspath(__file__))
    # args = parse_args()

    LOGGER.info("args: %s", args)

    from taichu_serve.model_server import load_service
    dict_model_service = {}

    model_path = os.path.abspath(args.model_path)
    # model_name = args.model_name

    model_service_file = args.service_file

    print(
        "model_path={} \n model_service_file={} "
        .format(model_path, model_service_file))

    if not os.path.exists(model_path):
        LOGGER.error("model_path not found.")
        sys.exit(1)
    if model_service_file is None:
        LOGGER.error("model_service_file not found.")
        sys.exit(1)
    # 检查model_service_file是否存在
    if model_service_file and not os.path.exists(os.path.join(model_path, model_service_file)):
        LOGGER.error("model_service_file not found.")
        sys.exit(1)

    module = load_service(os.path.join(model_path, model_service_file)
                          ) if model_service_file else ModelServer
    classes = [cls[1] for cls in inspect.getmembers(module, inspect.isclass)]

    # 如果没有自定义的ModelServer，则退出
    if len(classes) == 0:
        LOGGER.error("No user defined ModelServer found.")
        sys.exit(1)

    class_defs = list(
        filter(
            lambda c: issubclass(c, ModelServer) and len(
                c.__subclasses__()) == 0, classes))

    if len(class_defs) == 0:
        LOGGER.error("No user defined ModelServer found.")
        sys.exit(1)

    for c in class_defs:
        LOGGER.info("class_defs: %s", c.__name__)
        instance = c(model_path)
        # threading.Thread(target=instance.warmup).start()
        instance.warmup()
        dict_model_service[f'{str(c.__name__).lower()}_{instance.model_version.lower()}'] = instance

    # model_service = class_defs[0](model_path)
    status.value = 0
    LOGGER.info("model service init done")

    while True:
        data = pipe.recv()
        try:
            model_name = data.get('model_name')
            model_version = data.get('model_version')
            request_id = data.get('request_id', str(uuid.uuid4()))
            span_ctx = pickle.loads(data.get('span_ctx').encode('latin1'))

            Local.request_id = request_id
            LOGGER.info("[worker_main_loop] recv a request: %s", request_id)
            stream = False
            ins = dict_model_service.get(f'{model_name.lower()}_{model_version.lower()}', None)
            if ins is None:
                LOGGER.error("[worker_main_loop] model not found: %s", model_name)
                ret = {
                    'data': None,
                    'status': 'error',
                    'error': 'model not found',
                }
                pipe.send(ret)
                continue

            method = data.get('method', None)
            if method == 'destroy_context':
                LOGGER.info("[worker_main_loop] destroy context: %s", request_id)
                ins.destroy_context(request_id)

                ret = {'status': 'ok'}
                pipe.send(ret)
                continue

            stream = data.get('stream', False)
            resp = ins.inference(data.get('data'), request_id, span_ctx=span_ctx, stream=stream)
            cnt = 0
            if stream:
                for item in resp:
                    ret = {
                        'data': item,
                        'status': 'ok',
                    }
                    pipe.send(ret)
                    cnt += 1
            else:
                all_resp = []
                ret = {
                    'status': 'ok',
                }
                for item in resp:
                    all_resp.append(item)

                if len(all_resp) > 1:
                    LOGGER.error("[worker_main_loop] stream is false, but got more than one item")
                    data = {}
                    for index, item in enumerate(all_resp):
                        data[f'item_{index}'] = json.dumps(item)
                    ret['data'] = data

                if len(all_resp) == 0:
                    raise ModelPredictError("no response")

                if len(all_resp) == 1:
                    ret['data'] = all_resp[0]

                pipe.send(ret)

        except Exception as e:
            LOGGER.error(traceback.format_exc())
            ret = {
                'data': None,
                'status': 'error',
                'error': str(e),
            }
            pipe.send(ret)
        finally:
            if stream:
                pipe.send({
                    'status': 'end'
                })


@tracer.tracer.start_as_current_span("model_stream_inference")
def model_stream_inference(model_name, model_version, data, request_id, method=None):
    try:
        with tracer.tracer.start_as_current_span("pipe-acquire") as span:
            tracer.add_event(span=span, name="[model_stream_inference] pipe acquire start")
            p = workers_pipe.acquire(request_id)
            if p is None:
                raise TooManyRequestsError()
            tracer.add_event(span=span, name="[model_stream_inference] pipe acquire end")

        with tracer.tracer.start_as_current_span("pipe-send") as span:
            span_ctx = trace.get_current_span().get_span_context()
            payload = {'model_name': model_name, 'model_version': model_version, 'data': data,
                       'request_id': request_id, 'stream': True,
                       'span_ctx': pickle.dumps(span_ctx).decode('latin1')}
            if method:
                payload['method'] = method

            tracer.add_event(span=span, name="[model_stream_inference] pipe send")
            p.send(payload)
            while True:
                ret = p.recv()
                tracer.add_event(span=span, name="[model_stream_inference] pipe recv")
                if ret.get('status') == 'error':
                    tracer.add_event(span=span, name="[model_stream_inference] pipe error")
                    raise ModelPredictError(message=ret.get('error'))

                if ret.get('status') == 'end':
                    tracer.add_event(span=span, name="[model_stream_inference] pipe end")
                    return

                yield ret.get('data')

    finally:
        if p is not None:
            workers_pipe.release(request_id)


@tracer.tracer.start_as_current_span("model_inference")
def model_inference(model_name, model_version, data, request_id, method=None):
    try:
        with tracer.tracer.start_as_current_span("pipe-acquire") as span:
            tracer.add_event(span=span, name="[model_inference] pipe acquire start")
            p = workers_pipe.acquire(request_id)
            if p is None:
                LOGGER.info("no available worker")
                raise TooManyRequestsError()
            tracer.add_event(span=span, name="[model_inference] pipe acquire start")

        with tracer.tracer.start_as_current_span("pipe-send") as span:
            span_ctx = trace.get_current_span().get_span_context()
            payload = {'model_name': model_name, 'model_version': model_version, 'data': data,
                       'request_id': request_id, 'stream': False,
                       'span_ctx': pickle.dumps(span_ctx).decode('latin1')}
            if method:
                payload['method'] = method

            tracer.add_event(span=span, name="[model_inference] pipe send")
            p.send(payload)
            ret = p.recv()
            tracer.add_event(span=span, name="[model_inference] pipe recv")

            if ret.get('status') == 'error':
                raise ModelPredictError(message=ret.get('error'))
            return ret.get('data')

    finally:
        if p is not None:
            workers_pipe.release(request_id)


def init_model_service_instance():
    for i in range(args.instances_num):
        p1, p2 = multiprocessing.Pipe()
        status = multiprocessing.Value('i', -1)
        workers_status.append(status)
        LOGGER.info("start worker %s", i)
        multiprocessing.Process(target=worker_main_loop, args=(args, p2, status)
                                ).start()
        workers_pipe.append(p1)


def is_all_model_ready():
    if len(workers_status) != args.instances_num:
        return False
    for stat in workers_status:
        if stat.value != 0:
            return False

    return True


@app.before_request
def add_request_id():
    # 记录请求开始时间
    g.start = time.time()

    forwarded_for = request.headers.get('X-Forwarded-For')
    LOGGER.debug('X-Forwarded-For:{}'.format(forwarded_for))
    g.remote_addr = request.remote_addr
    if forwarded_for:
        g.remote_addr = forwarded_for.split(',')[0].strip()

    try:
        if 'x_request_id' in request.headers:
            request_id = request.headers.get('x_request_id')
        else:
            request_id = str(uuid.uuid4())
        setattr(g, 'request_id', request_id)
    except Exception as e:
        logging.error(str(e))


@app.before_request
def limiter():
    if request.path == '/health/live' or request.path == '/health/ready':
        return

    ok = semaphore.acquire(blocking=False)
    LOGGER.info('semaphore.acquire:{}'.format(ok))
    g.is_limited = not ok
    if not ok:
        return {'error': '请求过于频繁，请稍后再试'}, 429, {'Content-Type': 'application/json'}


@app.after_request
def after_request(response):
    if hasattr(g, 'is_limited') and not g.is_limited:
        semaphore.release()

    try:
        extra = {
            # 'id': str(uuid.uuid4()),
            'http_method': request.method,
            'endpoint': request.endpoint,
            'url_path': request.path,
            'url_query': request.query_string.decode('utf-8'),
            'host': request.host,
            'user_agent': '',
            'remote_addr': g.remote_addr,
            'content_type': request.content_type,
            'cost_time': round(time.time() - g.start, 3),
        }
        if 'user_agent' in request.headers:
            extra['user_agent'] = request.headers.get('user_agent')

        LOGGER.info('请求日志埋点', extra=extra)
    except Exception as e:
        LOGGER.error('{}\n{}'.format(repr(e), traceback.format_exc()))

    return response


@app.errorhandler(Exception)
def handle_exception(e):
    LOGGER.error('handle_exception: {}\n{}'.format(repr(e), traceback.format_exc()))
    if isinstance(e, ModelNotFoundError) or isinstance(e, ModelPredictError):
        return {'error': e.message}, 400, {'Content-Type': 'application/json'}

    return {'error': '系统内部错误，请联系维护人员'}, 400, {'Content-Type': 'application/json'}


@app.route('/health/live', methods=['GET'])
def live():
    ret = {'live': True}
    return json.dumps(ret, ensure_ascii=False), 200, {'Content-Type': 'application/json'}


@app.route('/health/ready', methods=['GET'])
def ready():
    is_ready = is_all_model_ready()
    ret = {'ready': is_ready}
    return json.dumps(ret, ensure_ascii=False), 200 if is_ready else 400, {'Content-Type': 'application/json'}


@app.route('/v2/models/<model_name>/versions/<model_version>/infer', methods=['POST'])
def predict(model_name, model_version):
    req = request.get_json()
    ctx = {}
    request_id = g.request_id

    ret = {
        'id': request_id,
        'model_name': model_name,
        'model_version': model_version,
        'parameters': {}
    }

    # instance = get_model_service(model_name, model_version)

    try:
        res = model_inference(model_name, model_version, req.get('parameters', {}), request_id)
    except TooManyRequestsError as e:
        LOGGER.info('Too many requests!')
        return {'error': '请求过于频繁，请稍后再试'}, 429, {'Content-Type': 'application/json'}
    except Exception as e:
        LOGGER.error('Algorithm crashed!')
        LOGGER.error(traceback.format_exc())
        raise ModelPredictError(message=str(e))

    ret['parameters'] = res
    return json.dumps(ret, ensure_ascii=False), 200, {
        'Content-Type': 'application/json'
    }


def get_result_json(ais_error):
    """
        Create a json response with error code and error message
    """
    data = ais_error.to_dict()
    data['words_result'] = {}

    return json.dumps(data, ensure_ascii=False)
