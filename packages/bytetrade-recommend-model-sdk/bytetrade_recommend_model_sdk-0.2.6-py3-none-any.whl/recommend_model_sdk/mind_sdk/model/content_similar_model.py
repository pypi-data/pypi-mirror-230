from recommend_model_sdk.tools.common_tool import CommonTool
from recommend_model_sdk.mind_sdk.config.content_similar_config import ContentSimilarConfig
from recommend_model_sdk.tools.aws_s3_tool import AWSS3Tool
from recommend_model_sdk.recommend.recommend_common_util import RecommendCommonUtil
from recommend_model_sdk.tools.weaviate_tool import WeaviateTool
from recommend_model_sdk.recommend.common_enum import RecommendSupportLanguageEnum,RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT

from datetime import datetime
import faiss

import numpy as np
import torch
import torch.nn.functional as F




class ContentSimilarModel:
    def __init__(self,config) -> None:
        if isinstance(config, ContentSimilarConfig) is False:
            raise ValueError("ContentSimilarModel is not model")
        self.__config = config
        self.__aws_tool = AWSS3Tool()
        self.__bucket_name = "gpu-model-data"
        
    def get_model_name(self):
        return self.__class__.__name__
    
    def get_single_news_vector(self,news_id):
        
        if isinstance(news_id,str) is False:
            raise ValueError(news_id is not str)
        if news_id == "PADDED_NEWS":
            return torch.zeros([self.__config.embedding_dim],dtype=torch.float32)
        current_key = f'{news_id}_{self.__config.embedding_model_name}_{self.__config.embedding_model_version}'
        current_embedding = self.__aws_tool.get_object_dict(self.__bucket_name,current_key)["dict"]["vec"]
        return torch.tensor(current_embedding)
    
    def get_sinle_user_vector(self, clicked_news_list,news2vector=None):
        if isinstance(clicked_news_list,list) is False:
            raise ValueError("clicked_news_list is not list")
        for current_news_id in clicked_news_list:
            if isinstance(current_news_id,str) is False:
                raise ValueError("current_new_id is not str")
            
        if news2vector is not None:
            if isinstance(news2vector,dict) is False:
                raise ValueError("news2vector is not dict")
            for current_item_id,current_embedding in news2vector.items():
                if isinstance(current_item_id,str) is False:
                    raise ValueError("current_item_id is not str")
                if isinstance(current_embedding,torch.Tensor) is False:
                    raise ValueError(f"current_item's embedding {current_item_id} is not tensor")
                if current_embedding.ndim != 1:
                    raise ValueError(f"current_item's embedding {current_item_id} dimension is not 1")
                if current_embedding.shape[0] != self.__config.embedding_dim:
                    raise ValueError(f"current_item's embedding {current_item_id} dimension element is not right")
        
        news_vector_list = list()
        for current_news_id in clicked_news_list:
            if news2vector is None:
                news_vector_list.append(self.get_single_news_vector(current_news_id))
            else:
                news_vector_list.append(news2vector[current_news_id])
        news_stack = torch.stack(news_vector_list, dim=0)
        news_sum = torch.sum(news_stack,dim=0)
        return news_sum

            
    
    def get_user_vector(self,clicked_news_vector):
        """
        Args:
            clicked_news_vector: batch_size, num_clicked_news_a_user, num_filters
        Returns:
            (shape) batch_size, num_filters
        """
        if isinstance(clicked_news_vector,torch.Tensor) is False:
            raise ValueError('clicked_news_vector is not torch.Tensor')
        tensor_shape = clicked_news_vector.shape
        if tensor_shape[1] != self.__config.num_clicked_news_a_user:
            raise ValueError("not correct clicked news number")
        if tensor_shape[2] != self.__config.embedding_dim:
            raise ValueError("not correct embedding dime")
        return torch.sum(clicked_news_vector,dim=1)
    
    def get_news_vector(self,news):
        """
        Args:
            news:
                {
                    "id": batch_size,
                }
        Returns:
            (shape) batch_size, embedding_dim
        """
        # batch_size, embedding_model
        if isinstance(news, dict) is False:
            raise ValueError("news is not dict")
     
        id_list = news["id"]
        if isinstance(id_list,list) is False:
            raise ValueError("id_list is not list")
        
        embedding_list = list()
        for current_news_id in id_list:        
            current_key = f'{current_news_id}_{self.__config.embedding_model_name}_{self.__config.embedding_model_version}'
            current_embedding_info =  self.__aws_tool.get_object_dict(self.__bucket_name,current_key)["dict"]
            if current_embedding_info["success"]:
                current_embedding = current_embedding_info["vec"]
                print(len(current_embedding))
            else:
                current_embedding = [0] * self.__config.embedding_dim
            embedding_list.append(current_embedding)
        tensor_embedding = torch.tensor(embedding_list)
        return tensor_embedding
        
    
    def get_prediction(self,candidate_news_vector,user_vec):
        if isinstance(candidate_news_vector,torch.Tensor) is False:
            raise ValueError("candidate_news_vector is not torch Tensor")
        if isinstance(user_vec, torch.Tensor) is False:
            raise ValueError("user_vec is not torch Tensor")
        if candidate_news_vector.ndim != 2:
            raise ValueError("candidate_news_vector ndim is not 2")
        if user_vec.ndim != 1:
            raise ValueError("user_vec ndim is not 1")
        if candidate_news_vector.shape[1] != self.__config.embedding_dim:
            raise ValueError("candidate_news_vector embedding dim is not right")
        if user_vec.shape[0] != self.__config.embedding_dim:
            raise ValueError("user_vec embedding dim is not right")       
        cos_sim = F.cosine_similarity(candidate_news_vector, user_vec, dim=1)
        return cos_sim
    
class ContentSimilarMultipleEmbeddingModelRecall:
    def __init__(self,base_document_id_to_list_embedding,config) -> None:
        self.__recommend_common_util = RecommendCommonUtil()
        self.__recommend_common_util.validate_base_document_id_to_item(base_document_id_to_list_embedding,True)
        if isinstance(config, ContentSimilarConfig) is False:
            raise ValueError("ContentSimilarModel is not model")
        self.__config = config
        set_shape = set()
        list_current_embedding = list()
        self.__base_length = len(base_document_id_to_list_embedding)
        self.__base_index_to_document_id = dict()
        self.__base_document_id_to_index_set = dict()
        self.__common_tool = CommonTool()
        self.__logger = self.__common_tool.get_logger()
        current_index = 0
        self.__base_document_id_to_created_at_tuple_list = list()
        for current_document_id, current_embedding_info in base_document_id_to_list_embedding.items():
            current_embedding_list = current_embedding_info["embedding"]
            created_at = current_embedding_info["created_at"]
            self.__base_document_id_to_created_at_tuple_list.append((current_document_id, created_at))
            for current_embedding in current_embedding_list:
                set_shape.add(current_embedding.shape)
                list_current_embedding.append(current_embedding)
                self.__base_index_to_document_id[current_index] = current_document_id
                if current_document_id not in self.__base_document_id_to_index_set:
                    self.__base_document_id_to_index_set[current_document_id] = set()
                self.__base_document_id_to_index_set[current_document_id].add(current_index)
                current_index = current_index + 1
                
        self.__base_document_id_to_created_at_tuple_list.sort(key=lambda tup: tup[1], reverse=True)
        #self.__logger.debug(self.__base_document_id_to_created_at_tuple_list)
        if len(set_shape) > 1:
            raise ValueError(f'have different shape embeddings')
        self.__embedding_shape = set_shape.pop()
        self.__original_base_embedding = np.stack(list_current_embedding)
        self.__normalized_base_embedding = np.copy(self.__original_base_embedding)
        faiss.normalize_L2(self.__normalized_base_embedding)
        # self.__original_base_embedding_index =  faiss.IndexFlatL2(self.__original_base_embedding)
        self.__cosin_index = faiss.index_factory(self.__embedding_shape[0], "Flat", faiss.METRIC_INNER_PRODUCT)
        self.__cosin_index.add(self.__normalized_base_embedding)
    
    

            
    def recall_empty(self,limit):
        result_tuple_list = list()
        for current_tuple in self.__base_document_id_to_created_at_tuple_list:
            result_tuple_list.append((current_tuple[0],0.5))
            if len(result_tuple_list) >= limit:
                break
        return result_tuple_list
    
    def recall(self,candidate_news_id_to_embedding_list,limit):
        """
        """
        if len(candidate_news_id_to_embedding_list) < 1:
            self.__logger.debug(f'candidate_news_id_to_embedding_list length samll than 1')
            return self.recall_empty(limit)
        self.__recommend_common_util.validate_candidate_document_id_to_item(candidate_news_id_to_embedding_list,self.__embedding_shape,True)
        # todo 
        # 
        result_tuple_list = []
        '''
        faiss.normalize_L2(user_embedding)
        consin_similar, nearest_indexes = self.__cosin_index.search(user_embedding, limit) # cosin similar,
        result_tuple_list = list()
        for current_similar,current_index in zip(consin_similar[0],nearest_indexes[0]):
              current_weight = (2 - (1 - current_similar)) * 1.0 / 2
              if current_index not in self.__base_index_to_document_id:
                  self.__logger.debug(f'current_index {current_index} is not exist')
                  continue
              result_tuple_list.append((self.__base_index_to_document_id[current_index],current_weight))
        
        if len(result_tuple_list)  < 1:
            self.__logger.debug('after complete result_tuple_list is small than 1')
            return self.recall_empty(limit)
        '''
        return result_tuple_list
              
              


class ContentSimilarModelRecall:
    def __init__(self,base_document_id_to_embedding,config) -> None:
        self.__recommend_common_util = RecommendCommonUtil()
        self.__recommend_common_util.validate_base_document_id_to_item(base_document_id_to_embedding)
        if isinstance(config, ContentSimilarConfig) is False:
            raise ValueError("ContentSimilarModel is not model")
        self.__config = config
        set_shape = set()
        list_current_embedding = list()
        self.__base_length = len(base_document_id_to_embedding)
        self.__base_index_to_document_id = dict()
        self.__base_document_id_to_index = dict()
        self.__common_tool = CommonTool()
        self.__logger = self.__common_tool.get_logger()
        current_index = 0
        self.__base_document_id_to_created_at_tuple_list = list()
        for current_document_id, current_embedding_info in base_document_id_to_embedding.items():
            current_embedding = current_embedding_info["embedding"]
            created_at = current_embedding_info["created_at"]
            self.__base_document_id_to_created_at_tuple_list.append((current_document_id, created_at))
            set_shape.add(current_embedding.shape)
            list_current_embedding.append(current_embedding)
            self.__base_index_to_document_id[current_index] = current_document_id
            self.__base_document_id_to_index[current_document_id] = current_index

            current_index = current_index + 1
        self.__base_document_id_to_created_at_tuple_list.sort(key=lambda tup: tup[1], reverse=True)
        #self.__logger.debug(self.__base_document_id_to_created_at_tuple_list)
        if len(set_shape) > 1:
            raise ValueError(f'have different shape embeddings')
        self.__embedding_shape = set_shape.pop()
        self.__original_base_embedding = np.stack(list_current_embedding)
        self.__normalized_base_embedding = np.copy(self.__original_base_embedding)
        faiss.normalize_L2(self.__normalized_base_embedding)
        # self.__original_base_embedding_index =  faiss.IndexFlatL2(self.__original_base_embedding)
        self.__cosin_index = faiss.index_factory(self.__embedding_shape[0], "Flat", faiss.METRIC_INNER_PRODUCT)
        self.__cosin_index.add(self.__normalized_base_embedding)
    
    
    def get_user_vector(self,candidate_news_id_to_embedding):
        current_list_embedding = list()
        for current_id, current_embedding_info in candidate_news_id_to_embedding.items():
            current_list_embedding.append(current_embedding_info['embedding'])
        if len(current_list_embedding) > self.__config.num_clicked_news_a_user:
            current_list_embedding = current_list_embedding[:self.__config.num_clicked_news_a_user]
        stack_candidate_embedding = np.stack(current_list_embedding)
        
        user_embedding = stack_candidate_embedding.sum(axis=0,keepdims=True)
        return user_embedding
            
    def recall_empty(self,limit):
        result_tuple_list = list()
        for current_tuple in self.__base_document_id_to_created_at_tuple_list:
            result_tuple_list.append((current_tuple[0],0.5))
            if len(result_tuple_list) >= limit:
                break
        return result_tuple_list
    
    def recall(self,candidate_news_id_to_embedding,limit):
        """
        """
        if len(candidate_news_id_to_embedding) < 1:
            self.__logger.debug(f'candidate_news_id_to_embedding length samll than 1')
            return self.recall_empty(limit)
        
        self.__recommend_common_util.validate_candidate_document_id_to_item(candidate_news_id_to_embedding,self.__embedding_shape)
        user_embedding = self.get_user_vector(candidate_news_id_to_embedding)
        faiss.normalize_L2(user_embedding)
        # self.__logger.debug(f'content user embedding shape {user_embedding.shape}')
        consin_similar, nearest_indexes = self.__cosin_index.search(user_embedding, limit) # cosin similar,
        result_tuple_list = list()
        for current_similar,current_index in zip(consin_similar[0],nearest_indexes[0]):
              current_weight = (2 - (1 - current_similar)) * 1.0 / 2
              if current_index not in self.__base_index_to_document_id:
                  self.__logger.debug(f'current_index {current_index} is not exist')
                  continue
              result_tuple_list.append((self.__base_index_to_document_id[current_index],current_weight))
        
        if len(result_tuple_list)  < 1:
            self.__logger.debug('after complete result_tuple_list is small than 1')
            return self.recall_empty(limit)
        return result_tuple_list
              
    

class WeaviateContentSimilarModelRecall:
    def __init__(self,config) -> None:
        
        self.__recommend_common_util = RecommendCommonUtil()
        self.__common_tool = CommonTool()
        self.__logger = self.__common_tool.get_logger()
        if isinstance(config, ContentSimilarConfig) is False:
            raise ValueError("ContentSimilarModel is not model")
        self.__config = config
        recommend_environment =self.__common_tool.get_default_environment_variable()
        if recommend_environment["weaviate_cloud"]:
            self.__weaviate_tool = WeaviateTool(model_root_dir=recommend_environment['model_path'],
                                                cloud=recommend_environment["weaviate_cloud"], 
                                                cloud_url=recommend_environment['cloud_weaviate_url'],
                                                cloud_api_key=recommend_environment['cloud_weaviate_api_key'],
                                                )
            self.__logger.debug("weaviate is cloud")
        else:
            self.__weaviate_tool = WeaviateTool(model_root_dir=recommend_environment['model_path'],
                                    cloud=recommend_environment["weaviate_cloud"], 
                                    private_ip=recommend_environment['private_weaviate_ip'],
                                    private_port=int(recommend_environment['private_weaviate_port']),
                                    )
            self.__logger.debug("weaviate is private")
        
        
        
    def get_user_vector(self,candidate_news_id_to_embedding):
        current_list_embedding = list()
        for current_id, current_embedding_info in candidate_news_id_to_embedding.items():
            current_list_embedding.append(current_embedding_info['embedding'])
        if len(current_list_embedding) > self.__config.num_clicked_news_a_user:
            current_list_embedding = current_list_embedding[:self.__config.num_clicked_news_a_user]
        stack_candidate_embedding = np.stack(current_list_embedding)
        
        user_embedding = stack_candidate_embedding.sum(axis=0,keepdims=True)
        return user_embedding
    
    def recall_empty(self,limit,major_language):
        current_language = RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT.get_langdetect_language_according_recommend_support_language(major_language)
        
        class_name = f'{self.__config.embedding_model_name}_{self.__config.embedding_model_version}_{current_language}'
        valid_class_name = self.__weaviate_tool.make_class_name_valid_name(class_name)
        sorted_tuple_list = self.__weaviate_tool.get_sort_uuid_and_published_at_and_cloud_id_tuple_of_one_class(valid_class_name)
        sorted_tuple_list.reverse()
        if len(sorted_tuple_list) > limit:
            sorted_tuple_list = sorted_tuple_list[:limit]
        result_list = list()
        for current_tuple in sorted_tuple_list:
            result_list.append((current_tuple[2],0.5))
        return result_list
    
    def recall(self,candidate_news_id_to_embedding,limit,
               package_range_list=None,start_time=None,end_time=None,
               major_language=None,category_list=None):
        """
        """
        if len(candidate_news_id_to_embedding) < 1:
            self.__logger.debug(f'candidate_news_id_to_embedding length samll than 1')
            return self.recall_empty(limit,major_language)

        self.__recommend_common_util.validate_candidate_document_id_to_item_for_weaviate(candidate_news_id_to_embedding,self.__config.embedding_dim)
        
        user_embedding = self.get_user_vector(candidate_news_id_to_embedding)
        # self.__logger.debug(f'weaviate user embedding shape {user_embedding.shape}')
        article_list = self.__weaviate_tool.search_nearest(self.__config.embedding_model_name,self.__config.embedding_model_version,limit,major_language,
                                                           embedding=user_embedding.tolist()[0],package_range_list=package_range_list
                                                           ,start_time=start_time,end_time=end_time,
                                                           category_list=category_list)
        self.__logger.debug(f'article_list {len(article_list)}')
        article_list.sort(key=lambda item:item['certainty'] , reverse=True) # here reverse is  true or false, is not important, because search nearest have got right result
        cloud_id_and_weight_tuple = list()
        for current_article in article_list:
            cloud_id_and_weight_tuple.append((current_article['cloud_id'],current_article['certainty']))
        return cloud_id_and_weight_tuple