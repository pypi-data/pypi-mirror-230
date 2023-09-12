import torch
import torch.nn as nn
from math import sqrt



from recommend_model_sdk.mind_sdk.config.content_similar_config import ContentSimilarConfig



class DNNClickPredictor(torch.nn.Module):
    def __init__(self, config,init_weight=False, hidden_size=None):
        super(DNNClickPredictor, self).__init__()
        if isinstance(config, ContentSimilarConfig) is False:
            raise ValueError("ContentSimilarModel is not model")
        self.__config = config

        input_size = 2*self.__config.embedding_dim
        if hidden_size is None: 
            hidden_size = int(sqrt(input_size))
        self.__dnn = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 1),
        )
        if init_weight:
            self.__dnn.apply(self.init_weights)
        
    def init_weights(self,m):
        if isinstance(m, nn.Linear):
            torch.nn.init.xavier_uniform(m.weight)
            m.bias.data.fill_(0.01)


    def forward(self, candidate_news_vector, user_vector):
        """
        Args:
            candidate_news_vector: batch_size, X
            user_vector: batch_size, X
        Returns:
            (shape): batch_size
        """
        # batch_size
        if isinstance(candidate_news_vector,torch.Tensor) is False:
            raise ValueError("candidate_news_vector  is not torch.Tensor")
        if candidate_news_vector.ndim != 2:
            raise ValueError("candidate_news_vector dimension is not 2")
        if candidate_news_vector.shape[1] != self.__config.embedding_dim:
            raise ValueError("candidate_news_vector dimension element is not right")
        
        if isinstance(user_vector,torch.Tensor) is False:
            raise ValueError("user_vector is not torch.Tensor")
        if user_vector.ndim != 2:
            raise ValueError("candidate_news_vector dimension is not 2")
        if user_vector.shape[1] != self.__config.embedding_dim:
            raise ValueError("candidate_news_vector dimension element is not right")
        
        if candidate_news_vector.shape[0] != user_vector.shape[0]:
            raise ValueError("candidate_news_vector and user_vector have different size")
        
        return self.__dnn(torch.cat((candidate_news_vector, user_vector),dim=1)).squeeze(dim=1)