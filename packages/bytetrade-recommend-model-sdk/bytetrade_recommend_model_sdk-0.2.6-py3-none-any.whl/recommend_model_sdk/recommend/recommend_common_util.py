from datetime import datetime
import numpy as np

class RecommendCommonUtil:
    def __init__(self) -> None:
        pass
    
    def validate_base_document_id_to_item(self,base_document_id_to_embedding,subdocument_embedding=False):
        if isinstance(base_document_id_to_embedding, dict) is False:
            raise ValueError("base_document_id_to_embedding is not dict")
        if len(base_document_id_to_embedding) < 1:
            raise ValueError('base_document_id_to_embedding length small than 1')
        for current_document_id, current_embedding_info in base_document_id_to_embedding.items():
            if isinstance(current_document_id, str) is False:
                raise ValueError(f"current_document_id {current_document_id} is not str")
            if isinstance(current_embedding_info, dict) is False:
                raise ValueError("current_embedding_info is not dict")
            if "embedding" not in current_embedding_info:
                raise ValueError("embedding not in current_embedding_info")
            
            if subdocument_embedding is False:   
                current_embedding = current_embedding_info["embedding"]
                # if isinstance(current_embedding,np.array)
                if isinstance(current_embedding, np.ndarray) is False:
                    raise ValueError('there is embedding is not np.ndarray')
                if current_embedding.dtype != np.float32:
                    raise ValueError("embedding_value is not float32")
            else:
                current_embedding_list = current_embedding_info["embedding"]
                if isinstance(current_embedding_list,list) is False:
                    raise ValueError("current_embedding_list is not list")
                for current_embedding in current_embedding_list:
                    if isinstance(current_embedding, np.ndarray) is False:
                        raise ValueError('there is embedding is not np.ndarray')
                    if current_embedding.dtype != np.float32:
                        raise ValueError("embedding_value is not float32")
                        
            if "created_at" not in current_embedding_info:
                raise ValueError("created_at not in current_embedding_info")
            created_at = current_embedding_info["created_at"]
            if isinstance(created_at, datetime) is False:
                raise ValueError("created_at is not datetime")
    
    def validate_candidate_document_id_to_item(self,document_id_to_document_info,base_embedding_shape,subdocument_embedding=False):
        if isinstance(document_id_to_document_info,dict) is False:
            raise ValueError('document_id_to_document_info is not dict')
        if isinstance(base_embedding_shape,tuple) is False:
            raise ValueError('base_embedding_shape is not tuple')
        for current_element in base_embedding_shape:
            if isinstance(current_element,int) is False:
                raise ValueError("current_element in tuple is not int")
            if current_element < 1:
                raise ValueError("current_element is small than 1")
        for current_document_id, current_embedding_info in document_id_to_document_info.items():
            if isinstance(current_document_id, str) is False:
                raise ValueError("current_document_id is not str")
            if isinstance(current_embedding_info, dict) is False:
                raise ValueError('current_embedding_info is not dict')
            if "embedding" not in current_embedding_info:
                raise ValueError("embedding not in current_embedding_info")
            
            if subdocument_embedding is False:
                current_embedding = current_embedding_info["embedding"]
                if isinstance(current_embedding, np.ndarray) is False:
                    raise ValueError('there is embedding is not np.ndarray')
                if current_embedding.dtype != np.float32:
                    raise ValueError("embedding_value is not float32")
                
                if current_embedding.shape != base_embedding_shape:
                    raise ValueError("embedding shape is not equal to shape in base embedding")
            else:
                current_embedding_list = current_embedding_info["embedding"]
                if isinstance(current_embedding_list,list) is False:
                    raise ValueError("current_embedding_list is not list")
                for current_embedding in current_embedding_list:
                    if isinstance(current_embedding, np.ndarray) is False:
                        raise ValueError('there is embedding is not np.ndarray')
                    if current_embedding.dtype != np.float32:
                        raise ValueError("embedding_value is not float32")
                    if current_embedding.shape != base_embedding_shape:
                        raise ValueError("embedding shape is not equal to shape in base embedding")
    
    def validate_candidate_document_id_to_item_for_weaviate(self,document_id_to_document_info,embedding_dim,subdocument_embedding=False):
        if isinstance(document_id_to_document_info,dict) is False:
            raise ValueError('document_id_to_document_info is not dict')
        if isinstance(embedding_dim,int) is False:
            raise ValueError('embedding_dim is not int')
        if embedding_dim < 1:
            raise ValueError("embedding_dim is small than 1")
        for current_document_id, current_embedding_info in document_id_to_document_info.items():
            if isinstance(current_document_id, str) is False:
                raise ValueError("current_document_id is not str")
            if isinstance(current_embedding_info, dict) is False:
                raise ValueError('current_embedding_info is not dict')
            if "embedding" not in current_embedding_info:
                raise ValueError("embedding not in current_embedding_info")
            
            if subdocument_embedding is False:
                current_embedding = current_embedding_info["embedding"]
                if isinstance(current_embedding, np.ndarray) is False:
                    raise ValueError('there is embedding is not np.ndarray')
                if current_embedding.dtype != np.float32:
                    raise ValueError("embedding_value is not float32")
                if current_embedding.shape[0] != embedding_dim:
                    raise ValueError("current_embedding's dimensions is not equal embedding dim")
            else:
                current_embedding_list = current_embedding_info["embedding"]
                if isinstance(current_embedding_list,list) is False:
                    raise ValueError("current_embedding_list is not list")
                for current_embedding in current_embedding_list:
                    if isinstance(current_embedding, np.ndarray) is False:
                        raise ValueError('there is embedding is not np.ndarray')
                    if current_embedding.dtype != np.float32:
                        raise ValueError("embedding_value is not float32")
                if current_embedding.shape[0] != embedding_dim:
                    raise ValueError("current_embedding's dimensions is not equal embedding dim")
    
    