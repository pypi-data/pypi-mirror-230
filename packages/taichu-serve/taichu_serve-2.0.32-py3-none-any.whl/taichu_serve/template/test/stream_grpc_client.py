import logging

import grpc
import taichu_serve.grpc_predict_v2_pb2 as grpc_predict_v2_pb2
import taichu_serve.grpc_predict_v2_pb2_grpc as grpc_predict_v2_pb2_grpc

model_name = "ModelService"


def guide_list_features(stub):
    num = 5

    while True:

        def generator():
            for i in range(num):
                req = grpc_predict_v2_pb2.ModelInferRequest()
                req.model_name = model_name
                req.model_version = '1'

                req.parameters['input'].bool_param = True
                yield req

                # time.sleep(1)

        resp = stub.ModelStreamInfer(generator())
        for feature in resp:
            print(feature)


def run():
    with grpc.insecure_channel('localhost:8080') as channel:
        stub = grpc_predict_v2_pb2_grpc.GRPCInferenceServiceStub(channel)
        guide_list_features(stub)


if __name__ == '__main__':
    logging.basicConfig()
    run()
