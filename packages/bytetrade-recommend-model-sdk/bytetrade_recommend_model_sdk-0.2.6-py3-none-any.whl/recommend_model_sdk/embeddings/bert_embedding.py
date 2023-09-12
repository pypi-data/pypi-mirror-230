import numpy as np
from sentence_transformers import SentenceTransformer
import torch

from langchain.text_splitter import CharacterTextSplitter


class BertEmbedding:
    def __init__(self) -> None:
        print( torch.cuda.is_available())
        self.__model = SentenceTransformer('all-MiniLM-L6-v2',device="cuda" if torch.cuda.is_available() else "cpu")
        self.__text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=10)
    
    def calculate_batch_document_embeddings(self, document_id_to_document):
        """_summary_

        Args:
            document_id_to_document (_type_): _description_

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        if isinstance(document_id_to_document, dict) is False:
            raise ValueError("document_id_to_document is not dict")
    
        
        list_document = []
        current_id_to_index =  dict()
        for current_id,current_document in document_id_to_document.items():
            if isinstance(current_id,str) is False:
                raise ValueError("current_id is not str")
            if isinstance(current_document,str) is False:
                raise ValueError("current_document is not str")
            list_document.append(current_document)
            current_id_to_index[current_id] = len(list_document) - 1
        
        

        list_document_embeddings = self.__model.encode(list_document, show_progress_bar=True)
        
        document_id_to_embedding = dict()
        for current_id in document_id_to_document.keys():
            document_id_to_embedding[current_id] = {
                   "success":True,
                   "vec":list_document_embeddings[current_id_to_index[current_id]]
            }
        return document_id_to_embedding
        
    
    def calculate_embedding(self,document):
        """_summary_

        Args:
            document (_type_): single document

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        if isinstance(document,str) is False:
            raise ValueError("document is not str")
        doc_embedding = self.__model.encode(document)
        result = dict()
        result["success"] = True
        result["vec"] = doc_embedding
        return result
    
    def calculate_document_embeddings_with_split_document(self,document):
        """_summary_
        
        Args:
            document (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
            {
                success:bool
                need_split:bool
                vec: when success is true, exist, numpy 
                subdoc_embedding_list: when success is true and need_split is true, exist, numpy
            }
        """
        if isinstance(document,str) is False:
            raise ValueError("document is not str")
        # print(document)
        list_document = self.__text_splitter.split_text(document)
        result = dict()
        if len(list_document) > 0:
            doc_embedding_list = self.__model.encode(list_document)
            result["need_split"] = True
            result["success"] = True
            result["subdoc_embedding_list"] = doc_embedding_list
            if len(list_document) > 1:
                cat_doc_embedding = np.stack(doc_embedding_list)
                result["vec"] = np.sum(cat_doc_embedding,axis = 0)
            else:
                result["vec"] = doc_embedding_list[0]
        else:
            result["success"] = False
            result["fail_reason"] = "when split document, there is not content"
            result["need_split"] = True
        
        return result
        