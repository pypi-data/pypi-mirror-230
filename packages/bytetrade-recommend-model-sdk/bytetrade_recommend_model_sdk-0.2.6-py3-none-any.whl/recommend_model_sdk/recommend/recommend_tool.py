import faiss
import numpy as np
from datetime import datetime


from recommend_model_sdk.tools.common_tool import CommonTool
from recommend_model_sdk.mind_sdk.config.content_similar_config import ContentSimilarConfig
from recommend_model_sdk.mind_sdk.model.content_similar_model import ContentSimilarModelRecall
from recommend_model_sdk.mind_sdk.model.content_similar_model import WeaviateContentSimilarModelRecall
from recommend_model_sdk.recommend.common_enum import VectorStoreEnum,RecommendSupportLanguageEnum,RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT
from recommend_model_sdk.recommend.rank_tool import CTRRankTool
from recommend_model_sdk.tools.weaviate_tool import WeaviateTool

class RecommendTool:

    def __init__(self, base_document_id_to_embedding,
                 pretrained_item_embedding_model_name,
                 pretrained_item_embedding_model_version,vector_store = VectorStoreEnum.FAISS) -> None:
        """_summary_
        if vector_store is WEAVIATE:
            WEAVIATE IS NOT NECESSARY, can pass a empty dict {}
        else:
            pass
        

        Args:
            base_document_id_to_embedding (_type_): _description_
            {
                "document_id":{
                    "embedding":[],numpy
                    "created_at": datetime
                }
            }

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """
        if isinstance(vector_store,VectorStoreEnum) is False:
            raise ValueError("vector_store is not VectorStoreEnum")
        self.__vector_store = vector_store
        content_config = ContentSimilarConfig(pretrained_item_embedding_model_name,pretrained_item_embedding_model_version)
        self.__model_name = pretrained_item_embedding_model_name
        self.__model_version = pretrained_item_embedding_model_version
        self.__content_config = content_config
        if self.__vector_store == VectorStoreEnum.FAISS:
            self.__faiss_content_similar_model = ContentSimilarModelRecall(base_document_id_to_embedding,content_config)
        elif self.__vector_store == VectorStoreEnum.WEAVIATE:
            self.__weaviate_content_similar_model = WeaviateContentSimilarModelRecall(content_config)
        self.__common_tool = CommonTool()
        self.__logger = self.__common_tool.get_logger()
        environment_variable = self.__common_tool.get_default_environment_variable()
        model_root_dir = environment_variable["model_path"]
        weaviate_cloud = environment_variable["weaviate_cloud"]
        private_weaviate_ip = environment_variable["private_weaviate_ip"]
        private_weaviate_port = environment_variable["private_weaviate_port"]
        
        self.__ctr_rank_tool = CTRRankTool(model_root_dir)
        self.__weaviate_tool = WeaviateTool(model_root_dir,weaviate_cloud,private_ip=private_weaviate_ip,private_port=private_weaviate_port)

    
    def __recall_content_similar(self,candidate_document_id_to_document_info,limit = 100,
                                 package_range_list=None,start_time=None,end_time=None,
                                 major_language=None,category_list=None):
        if self.__vector_store == VectorStoreEnum.FAISS:
            url_weight_tuple_list = self.__faiss_content_similar_model.recall(candidate_document_id_to_document_info,limit)
        elif self.__vector_store == VectorStoreEnum.WEAVIATE:
            url_weight_tuple_list = self.__weaviate_content_similar_model.recall(candidate_document_id_to_document_info,limit,package_range_list,start_time,end_time,major_language,category_list)
            
        return url_weight_tuple_list
    
    def __rank_content_similar(self,cloud_id_weight_tuple_list,major_language=None):
        rank_cloud_id_weight_tuple_list = list()
        if self.__vector_store == VectorStoreEnum.WEAVIATE:
            if major_language is None:
                raise ValueError("when vector store is weaviate, major_language is must")
            if isinstance(major_language,RecommendSupportLanguageEnum) is False:
                raise ValueError("major_language is not RecommendSupportLanguageEnum")
            str_recommend_language = RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT.get_langdetect_language_according_recommend_support_language(major_language)
            for current_batch_cloud_id_weight_tuple_list in self.__common_tool.batch_next(cloud_id_weight_tuple_list,100):
                self.__logger.debug(f'current_batch cloud_id_weight_tuple {current_batch_cloud_id_weight_tuple_list}')
                cloud_id_to_weight = dict()
                for current_cloud_id,current_weight in current_batch_cloud_id_weight_tuple_list:
                    cloud_id_to_weight[current_cloud_id] = current_weight
                cloud_id_list = list(cloud_id_to_weight.keys())
                current_article_list = self.__weaviate_tool.search_nearest(self.__model_name,self.__model_version,10000,major_language,cloud_id_list=cloud_id_list,fetch_vector=True)
                current_embeeding_list = list()
                for current_article in current_article_list:
                    current_embeeding_list.append(current_article["vector"])
                current_embedding_array = np.array(current_embeeding_list)
                whether_can_predict = self.__ctr_rank_tool.whether_can_predict(current_embedding_array,self.__model_name,self.__model_version)
                if whether_can_predict is False:
                    self.__logger.debug(f'whether_can_predict {whether_can_predict}')
                    return cloud_id_weight_tuple_list
                label_list,proba_list = self.__ctr_rank_tool.predict(current_embedding_array,self.__model_name,self.__model_version)
                for current_article,current_click_proba in zip(current_article_list,proba_list):
                    current_cloud_id = current_article["cloud_id"]
                    current_recall_weight = cloud_id_to_weight[current_cloud_id]
                    rank_weight = (current_click_proba + current_recall_weight)*1.0 / 2
                    rank_cloud_id_weight_tuple_list.append((current_cloud_id,rank_weight))
        else:
            raise ValueError("use faiss not support rank")
        rank_cloud_id_weight_tuple_list.sort(key=lambda a: a[1],reverse=True)
        return rank_cloud_id_weight_tuple_list
                    
                
            
    
    def recommend(self,candidate_document_id_to_document_info,rank_limit=100,
                  start_time=None,end_time=None,
                  major_language=None,category_list=None):
        """_summary_

        Args:
            candidate_document_id_to_document_info (_type_): _description_
            rank_limit (int, optional): _description_. Defaults to 100.
            package_range_list (_type_, optional): _description_. Defaults to None. [str,str]
            start_time (_type_, optional): _description_. Defaults to None. datetime
            end_time (_type_, optional): _description_. Defaults to None. dateime 
            major_language (_type_, optional): _description_. Defaults to None. 
            category_list (_type_, optional): _description_. Defaults to None. [str,str,str]

        Returns:
            _type_: _description_
        """
        if self.__vector_store == VectorStoreEnum.WEAVIATE:
            if major_language is None:
                raise ValueError("when vector store is weaviate, major_language is must")
        self.__logger.debug(f'major_language {major_language}')
        url_weight_tuple_list = self.__recall_content_similar(candidate_document_id_to_document_info,rank_limit,package_range_list=None,
                                             start_time=start_time,end_time=end_time,major_language=major_language,
                                             category_list=category_list)
        url_to_recall_score = dict()
        for current_tuple in url_weight_tuple_list:
            url_to_recall_score[current_tuple[0]] = current_tuple[1]
            
        self.__logger.debug(f'recall tuple list {len(url_weight_tuple_list)}')
        if self.__vector_store == VectorStoreEnum.FAISS:
            return url_weight_tuple_list
        else:
            rank_weight_tuple_list = self.__rank_content_similar(url_weight_tuple_list,major_language)
            # self.__logger.debug(f'recall cloud id weith tuple list {url_weight_tuple_list}')
            # self.__logger.debug(f'rank weight tuple list {rank_weight_tuple_list}')
            new_rank_weight_tuple_list = list()
            for current_tuple in rank_weight_tuple_list:
                new_rank_weight_tuple_list.append((current_tuple[0],current_tuple[1],url_to_recall_score[current_tuple[0]]))
            return new_rank_weight_tuple_list
        
        
        
        
    
    def train_ctr_rank_model(self,positive_entry_id_set,negative_entry_id_set,model_name,model_version,method_according_entry_id_and_label_to_get_embedding,duration_max=1200):
        self.__ctr_rank_tool.train(positive_entry_id_set,negative_entry_id_set,model_name,model_version,method_according_entry_id_and_label_to_get_embedding,duration_max)