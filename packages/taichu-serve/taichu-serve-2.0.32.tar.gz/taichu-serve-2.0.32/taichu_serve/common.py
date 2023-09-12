import functools
import logging
import threading
import time
import uuid

import grpc

from taichu_serve.error_code import ModelPredictError, ModelNotFoundError

Local = threading.local()
logger = logging.getLogger(__name__)


def grpc_interceptor(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        context = args[2]
        start_time = time.time()
        try:
            ret = func(*args, **kwargs)
        except ModelPredictError as e:
            logger.error('[grpc_interceptor] error: %s', e.message)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(e.message)
        except ModelNotFoundError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(e.message)

        logger.info('[grpc_interceptor] cost: %s', time.time() - start_time)
        return ret

    return wrapper
