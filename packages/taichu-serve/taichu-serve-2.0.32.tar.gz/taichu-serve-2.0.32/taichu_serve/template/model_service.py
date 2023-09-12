import logging
from taichu_serve import ModelServer

logger = logging.getLogger(__name__)


class ModelService(ModelServer):
    def __init__(self, model_path):
        super(ModelService, self).__init__(model_path)
        logger.info("self.model_path: %s",
                    model_path)

    def _preprocess(self, input_data, context):
        logger.info('enter _preprocess')

        return input_data

    def _inference(self, preprocessed_result, context):
        logger.info('enter _inference')

        return preprocessed_result

    def _postprocess(self, inference_result, context):
        logger.info('enter _postprocess')

        return inference_result

    def _warmup(self):
        logger.info('warmup finished')


if __name__ == '__main__':
    app = ModelService("path/to/model")
    app.run(http_port=8081, grpc_port=8080)
