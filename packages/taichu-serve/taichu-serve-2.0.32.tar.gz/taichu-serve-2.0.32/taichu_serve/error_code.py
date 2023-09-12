"""
modelarts service error code definition
"""
from collections import OrderedDict


class ModelArtsError(Exception):
    'Base class for AIS exceptions'
    code_key = 'erno'
    msg_key = 'msg'
    code = NotImplemented
    msg = NotImplemented

    def to_dict(self):
        'convert to an OrderedDict that can be used to update json result'
        return OrderedDict([[self.code_key, self.code],
                            [self.msg_key, self.msg]])

    def __str__(self):
        return 'AISError: (%s, %s)' % (self.code, self.msg)


class ModelNotFoundError(Exception):
    def __init__(self, code='ModelNotFoundError', message='Model not found'):
        self.code = code
        self.message = message


class ModelPredictError(Exception):
    def __init__(self, code='ModelPredictError', message='Model predict error'):
        self.code = code
        self.message = message

    def __str__(self):
        return self.message


class TooManyRequestsError(Exception):
    def __init__(self, code='TooManyRequestsError', message='Too many requests'):
        self.code = code
        self.message = message

    def __str__(self):
        return self.message


class MR0100(ModelArtsError):
    'Specific ModelArts error'
    code = 'MR.0100'
    msg = 'Succeeded'


class MR0101(ModelArtsError):
    'Specific ModelArts error'
    code = 'MR.0101'
    msg = 'The input parameter is invalid'


class MR0105(ModelArtsError):
    'Specific ModelArts error'
    code = 'MR.0105'
    msg = 'Recognition failed'
