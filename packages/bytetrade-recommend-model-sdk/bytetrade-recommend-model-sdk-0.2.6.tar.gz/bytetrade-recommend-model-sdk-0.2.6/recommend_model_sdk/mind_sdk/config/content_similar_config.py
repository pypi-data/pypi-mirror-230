from recommend_model_sdk.tools.common_tool import CommonTool
from recommend_model_sdk.mind_sdk.config.mind_base_config import MINDBaseConfig

class ContentSimilarConfig(MINDBaseConfig):
    dataset_attributes = {"news": [], "record": []}
    def __init__(self,embedding_model_name,embedding_model_version) -> None:
        super().__init__()
        self.__common_tool = CommonTool()
        model_info = self.__common_tool.valid_model_name_and_version(embedding_model_name,embedding_model_version)
        self.embedding_model_name = embedding_model_name
        self.embedding_model_version = embedding_model_version
        self.embedding_dim = model_info["embedding_dim"]