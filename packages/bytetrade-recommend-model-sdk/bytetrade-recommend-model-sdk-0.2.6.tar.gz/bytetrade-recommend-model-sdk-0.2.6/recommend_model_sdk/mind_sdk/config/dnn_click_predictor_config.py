from recommend_model_sdk.mind_sdk.config.content_similar_config import ContentSimilarConfig
class DNNClickPredictorConfig(ContentSimilarConfig):
    def __init__(self, embedding_model_name, embedding_model_version) -> None:
        super().__init__(embedding_model_name, embedding_model_version)
        self.batch_size = 4
        self.num_epochs = 100
        self.learning_rate = 1e-5
        