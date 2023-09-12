"""`ModelService` defines an API for base model service.
"""
from __future__ import print_function

import logging
import os
import sys
import traceback
from abc import ABCMeta, abstractmethod
import time

logger = logging.getLogger(__name__)


class BaseModelService(object):
    '''ModelService wraps up all preprocessing, inference and postprocessing
    functions used by model service. It is defined in a flexible manner to
    be easily extended to support different frameworks.
    '''
    __metaclass__ = ABCMeta

    def __init__(self, model_path):
        self.model_path = model_path

    @abstractmethod
    def inference(self, data, request_id, span_ctx, stream=False):
        '''
        Wrapper function to run preprocess, inference and postprocess functions.

        Parameters
        ----------
        data : map of object
            Raw input from request.

        Returns
        -------
        list of outputs to be sent back to client.
            data to be sent back
        '''
        pass

    @abstractmethod
    def ping(self):
        '''Ping to get system's health.

        Returns
        -------
        String
            A message, "health": "healthy!", to show system is healthy.
        '''
        pass

    @abstractmethod
    def signature(self):
        '''Signiture for model service.

        Returns
        -------
        Dict
            Model service signiture.
        '''
        pass


# class SingleNodeService(BaseModelService):
#     '''SingleNodeModel defines abstraction for model service which loads a
#     single model.
#     '''
#
#     def __init__(self, model_path):
#         super(SingleNodeService, self).__init__(model_path)
#         self._ready = False
#
#     def warmup(self):
#         start_time = time.time()
#         self._warmup()
#         self._ready = True
#         logger.info('warmup time: ' + str((time.time() - start_time) * 1000) + 'ms')
#
#     def inference(self, data, context={}):
#         '''
#         Wrapper function to run preprocess, inference and postprocess functions.
#
#         Parameters
#         ----------
#         data : map of object
#             Raw input from request.
#
#         Returns
#         -------
#         list of outputs to be sent back to client.
#             data to be sent back
#         '''
#         pre_start_time = time.time()
#         data = self._preprocess(data, context=context)
#         infer_start_time = time.time()
#
#         # Update preprocess latency metric
#         pre_time_in_ms = (infer_start_time - pre_start_time) * 1000
#         logger.info('preprocess time: ' + str(pre_time_in_ms) + 'ms')
#
#         data = self._inference(data, context=context)
#         infer_end_time = time.time()
#         infer_in_ms = (infer_end_time - infer_start_time) * 1000
#
#         logger.info('infer time: ' + str(infer_in_ms) + 'ms')
#         data = self._postprocess(data, context=context)
#
#         # Update inference latency metric
#         post_time_in_ms = (time.time() - infer_end_time) * 1000
#         logger.info('postprocess time: ' + str(post_time_in_ms) + 'ms')
#
#         logger.info('latency: ' + str(pre_time_in_ms + infer_in_ms + post_time_in_ms) + 'ms')
#         return data
#
#     @abstractmethod
#     def _inference(self, data, context={}):
#         '''
#         Internal inference methods. Run forward computation and
#         return output.
#
#         Parameters
#         ----------
#         data : map of NDArray
#             Preprocessed inputs in NDArray format.
#
#         Returns
#         -------
#         list of NDArray
#             Inference output.
#         '''
#         return data
#
#     @abstractmethod
#     def _preprocess(self, data, context={}):
#         '''
#         Internal preprocess methods. Do transformation on raw
#         inputs and convert them to NDArray.
#
#         Parameters
#         ----------
#         data : map of object
#             Raw inputs from request.
#
#         Returns
#         -------
#         list of NDArray
#             Processed inputs in NDArray format.
#         '''
#         return data
#
#     @abstractmethod
#     def _postprocess(self, data, context={}):
#         '''
#         Internal postprocess methods. Do transformation on inference output
#         and convert them to MIME type objects.
#
#         Parameters
#         ----------
#         data : map of NDArray
#             Inference output.
#
#         Returns
#         -------
#         list of object
#             list of outputs to be sent back.
#         '''
#         return data
#
#     @abstractmethod
#     def _warmup(self):
#         pass
#
#     @property
#     def model_version(self):
#         return '1'
#
#     @property
#     def ready(self):
#         return self._ready
#

def load_service(path, name=None):
    sys.path.append(os.path.dirname(path))

    try:
        if not name:
            name = os.path.splitext(os.path.basename(path))[0]

        module = None
        if sys.version_info[0] > 2:
            import importlib
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        else:
            import imp
            module = imp.load_source(name, path)

        return module
    except Exception:
        traceback.print_exc()
        raise Exception('Incorrect or missing service file: ' + path)
