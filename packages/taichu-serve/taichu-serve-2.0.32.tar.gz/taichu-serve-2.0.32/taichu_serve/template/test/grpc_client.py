import grpc
import taichu_serve.grpc_predict_v2_pb2 as grpc_predict_v2_pb2
import taichu_serve.grpc_predict_v2_pb2_grpc as grpc_predict_v2_pb2_grpc

model_name = "ModelService"


def run():
    conn = grpc.insecure_channel('localhost:8080')
    client = grpc_predict_v2_pb2_grpc.GRPCInferenceServiceStub(channel=conn)

    req = grpc_predict_v2_pb2.ModelInferRequest()
    req.model_name = model_name
    req.model_version = '1'
    req.parameters['boo_var'].bool_param = True
    req.parameters['float_var'].float_param = 12.3432
    req.parameters['str_var'].string_param = 'str'

    respnse = client.ModelInfer(req)
    print("received:", respnse)


if __name__ == '__main__':
    run()
