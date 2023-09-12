from datetime import datetime
import numpy as np
from tqdm import tqdm
import weaviate
from weaviate.util import generate_uuid5

from recommend_model_sdk.tools.common_tool import CommonTool
from recommend_model_sdk.tools.model_tool import ModelTool
from recommend_model_sdk.recommend.common_enum import RecommendSupportLanguageEnum,RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT
from recommend_model_sdk.recommend.recommend_common_util import RecommendCommonUtil

class WeaviateTool:
    """
    use cloud_id instead relpace url
    """
    def __init__(self,model_root_dir,cloud,cloud_url=None,cloud_api_key=None,private_ip=None,private_port=None) -> None:
        if isinstance(cloud,bool) is False:
            raise ValueError("cloud is not bool")
        if cloud:
            if isinstance(cloud_url,str) is False:
                raise ValueError("url is not str")
            if isinstance(cloud_api_key,str) is False:
                raise ValueError("api_key is not str")
            self.__client = weaviate.Client(url=cloud_url,auth_client_secret=weaviate.AuthApiKey(api_key=cloud_api_key))
        else:
            if isinstance(private_ip,str) is False:
                raise ValueError("private_ip is not str")
            if isinstance(private_port,int) is False:
                raise ValueError("private_port is not int ")
            self.__client = weaviate.Client(url=f'http://{private_ip}:{private_port}')
            
        
        self.__model_tool = ModelTool(model_root_dir)
        self.__common_tool = CommonTool()
        self.__logger = self.__common_tool.get_logger()
        self.__feed_id_to_feed = self.__model_tool.download_latest_all_feed()
        self.__category_name_to_category = self.__model_tool.download_latest_all_category()
        self.__class_properties = set()
        # self.__class_properties.add("url")
        self.__class_properties.add("published_at")
        # self.__class_properties.add("package_id")
        self.__class_properties.add("subdoc_index")
        self.__class_properties.add("first_level_category")
        # self.__class_properties.add("second_level_category")
        self.__class_properties.add("major_language") # not property
        # self.__class_properties.add("keyword_list")
        # self.__class_properties.add("filtered")
        self.__class_properties.add("cloud_id")
        self.__class_properties.add("feed_id")
        self.__support_language_set = RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT.get_all_lang_detect_language_set()
        self.__recommend_common_tool = RecommendCommonUtil()
        
    def get_class_properties(self):
        return self.__class_properties  
    
    def init_class_according_specific_class_name(self,class_name,ef=None,ef_construction=None,max_connections=None,vector_cache_max_objects=None,metadata=True):
        class_name_set = self.get_all_class()
        if class_name in class_name_set:
            self.__logger.debug(f'class {class_name} is already exist')
            return
        vector_index_config = dict()
        if ef is not None:
            if isinstance(ef,int) is False:
                raise ValueError("ef is not int")
            if ef < -1:
                raise ValueError("ef should greater than -1")
            vector_index_config["ef"] = ef
            
        if ef_construction is not None:
            if isinstance(ef_construction,int) is False:
                raise ValueError("ef_construction is not int")
            if ef_construction <= 0:
                raise ValueError("ef_construction greater than 0")
            vector_index_config["efConstruction"] = ef_construction
    
            
        if max_connections is not None:
            if isinstance(max_connections,int) is False:
                raise ValueError("max_connections is not int")
            if max_connections <= 0:
                raise ValueError("max_connection should greater than 0")
            vector_index_config["maxConnections"] = max_connections
            
        
        if vector_cache_max_objects is not None:
            if isinstance(vector_cache_max_objects,int) is False:
                raise ValueError("vector_cache_max_objects is not int")
            if vector_cache_max_objects <= 0:
                raise ValueError("vector_cache_max_objects should greater than 0")
            vector_index_config["vectorCacheMaxObjects"] = vector_cache_max_objects
        '''
        class_obj = {
            "class":f'{model_name}_{model_version}',
            'properties':[
                {
                    'name':'url', # for secrete
                    'dataType':['text'],
                },
                {
                    'name':'published_at',
                    'dataType':['date'],
                },
                {
                    'name':'package_id',
                    'dataType':['text'],
                },
                {
                    'name':'subdoc_index',
                    'dataType':['int'], # if subdoc_index is -1, represent it is summary embedding, not subdoc embedding
                },
                {
                    'name':'first_level_category',
                    'dataType':['text'], # category two level, which level
                },
                {
                    'name':'second_level_category',
                    'dataType':['text'], # category second level, which level
                },
                {
                    'name':'major_language',
                    'dataType':['text'],
                },
                {
                    'name':'keyword_list',
                    'dataType':['text[]'],
                },
                {
                    'name':'filtered',
                    'dataType':['boolean']
                },
                {
                    'name':'cloud_id',
                    'dataType':['int']
                }
            ],

        }
        '''
        
        simple_class_properties = [
                {
                    'name':'subdoc_index',
                    'dataType':['int'], # if subdoc_index is -1, represent it is summary embedding, not subdoc embedding
                },
                {
                    'name':'first_level_category',
                    'dataType':['int'], # category two level, which level
                },
                {
                    'name':'published_at',
                    'dataType':['int'],
                },
                {
                    'name':'cloud_id',
                    'dataType':['int']
                },
                {
                    'name':'feed_id',
                    'dataType':['int']
                }
        ]
        class_obj = dict()
        class_obj["class"] = class_name
        if metadata is True:
            class_obj["properties"] = simple_class_properties
            
        if len(vector_index_config) > 0:
            class_obj["vectorIndexConfig"] = vector_index_config
        self.__client.schema.create_class(class_obj)
    
    def init_class(self,model_name,model_version,ef=None,ef_construction=None,max_connections=None,vector_cache_max_objects=None,metadata=True):
        # text,image,model_name, model_version, include, image, text, video, audio
        # https://weaviate.io/developers/weaviate/config-refs/datatypes weaviate_type
        vector_index_config = dict()
        if ef is not None:
            if isinstance(ef,int) is False:
                raise ValueError("ef is not int")
            if ef < -1:
                raise ValueError("ef should greater than -1")
            vector_index_config["ef"] = ef
            
        if ef_construction is not None:
            if isinstance(ef_construction,int) is False:
                raise ValueError("ef_construction is not int")
            if ef_construction <= 0:
                raise ValueError("ef_construction greater than 0")
            vector_index_config["efConstruction"] = ef_construction
    
            
        if max_connections is not None:
            if isinstance(max_connections,int) is False:
                raise ValueError("max_connections is not int")
            if max_connections <= 0:
                raise ValueError("max_connection should greater than 0")
            vector_index_config["maxConnections"] = max_connections
            
        
        if vector_cache_max_objects is not None:
            if isinstance(vector_cache_max_objects,int) is False:
                raise ValueError("vector_cache_max_objects is not int")
            if vector_cache_max_objects <= 0:
                raise ValueError("vector_cache_max_objects should greater than 0")
            vector_index_config["vectorCacheMaxObjects"] = vector_cache_max_objects
        '''
        class_obj = {
            "class":f'{model_name}_{model_version}',
            'properties':[
                {
                    'name':'url', # for secrete
                    'dataType':['text'],
                },
                {
                    'name':'published_at',
                    'dataType':['date'],
                },
                {
                    'name':'package_id',
                    'dataType':['text'],
                },
                {
                    'name':'subdoc_index',
                    'dataType':['int'], # if subdoc_index is -1, represent it is summary embedding, not subdoc embedding
                },
                {
                    'name':'first_level_category',
                    'dataType':['text'], # category two level, which level
                },
                {
                    'name':'second_level_category',
                    'dataType':['text'], # category second level, which level
                },
                {
                    'name':'major_language',
                    'dataType':['text'],
                },
                {
                    'name':'keyword_list',
                    'dataType':['text[]'],
                },
                {
                    'name':'filtered',
                    'dataType':['boolean']
                },
                {
                    'name':'cloud_id',
                    'dataType':['int']
                }
            ],

        }
        '''
        
        simple_class_properties = [
                {
                    'name':'subdoc_index',
                    'dataType':['int'], # if subdoc_index is -1, represent it is summary embedding, not subdoc embedding
                },
                {
                    'name':'first_level_category',
                    'dataType':['int'], # category two level, which level
                },
                {
                    'name':'published_at',
                    'dataType':['int'],
                },
                {
                    'name':'cloud_id',
                    'dataType':['int']
                },
                                {
                    'name':'feed_id',
                    'dataType':['int']
                }
        ]
        class_obj = dict()
        if metadata is True:
            class_obj["properties"] = simple_class_properties
            
        if len(vector_index_config) > 0:
            class_obj["vectorIndexConfig"] = vector_index_config
        
        class_name_set = self.get_all_class()
        
        for current_language in self.__support_language_set:
            class_name = f'{model_name}_{model_version}_{current_language}'
            class_name = self.make_class_name_valid_name(class_name)
            if class_name in class_name_set:
                continue
            self.__logger.debug(f'create class {class_name}')
            class_obj['class'] = class_name
            self.__client.schema.create_class(class_obj)
            self.__logger.debug(f'create class {class_name} success')

    
    def delete_class_according_model_name_and_model_version(self,model_name,model_version):
        class_name = f'{model_name}_{model_version}'
        for current_language in self.__support_language_set:
            class_name = f'{model_name}_{model_version}_{current_language}'
            self.__logger.debug(f'delete class {class_name}')
            class_name = self.make_class_name_valid_name(class_name)
            self.__client.schema.delete_class(class_name)  
            self.__logger.debug(f'delete class {class_name} success')
        
    def delete_class_according_class_name(self,class_name):
        if isinstance(class_name,str) is False:
            raise ValueError("class_name is not str")
        all_class_name_set = self.get_all_class()
        if class_name not in all_class_name_set:
            raise ValueError(f"class_name is not valid")
        self.__client.schema.delete_class(class_name)  
        self.__logger.debug(f'delete class {class_name} success')
    
    def insert_package_data_list(self,package_info_list,target_model_name,target_model_version,metadata=True,capacity=10000,overload_delete=True,black_feed_set=None):
        if black_feed_set is not None:
            if isinstance(black_feed_set,set) is False:
                raise ValueError("black_feed_set is not set")
            for current_feed in black_feed_set:
                if isinstance(current_feed,int) is False:
                    raise ValueError("current_feed is not int")
                
        if isinstance(package_info_list,list) is False:
            raise ValueError("package_info_list is not list")
        merge_url_to_success_info = dict()
        for current_package_info in package_info_list:
            url_to_success_info,overload_delete_uuid_to_cloud_id = self.insert_package_data(current_package_info,target_model_name,target_model_version,metadata=metadata,capacity=capacity,overload_delete=False,black_feed_set=black_feed_set)
            merge_url_to_success_info.update(url_to_success_info)
        overload_delete_uuid_to_cloud_id = dict()
        if overload_delete:
            overload_delete_uuid_to_cloud_id = self.delete_overload_data_according_latest_embedding(target_model_name,target_model_version,capacity,{})   
        return url_to_success_info,overload_delete_uuid_to_cloud_id
            
    
    def insert_package_data(self,package_info,target_model_name,target_model_version,metadata=True,capacity=10000,overload_delete=True,black_feed_set=None):
        """_summary_

        Args:
            package_info (_type_): _description_
            {
                "main_language":
                "model_name":
                "model_version":
                "package_id":
                
            }
            target_model_name (_type_): _description_
            target_model_version (_type_): _description_

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_

        Returns:
            _type_: _description_
            {
                url:{
                    "success": bool
                    "fail_reason": ["",""], if success if True
                    "cloud_id": int
                    "uuids":{
                        "subdoc": uuid   # subdoc 
                    }
                    
                }
            }
        """
        if black_feed_set is not None:
            if isinstance(black_feed_set,set) is False:
                raise ValueError("black_feed_set is not set")
            for current_feed in black_feed_set:
                if isinstance(current_feed,int) is False:
                    raise ValueError("current_feed is not int")
                
        if isinstance(package_info,dict) is False:
            raise ValueError("package_info is not dict")
        
        if "package_id" not in package_info:
            raise ValueError("package_id is not exist")
        current_pacakge_id = package_info["package_id"]
        if isinstance(current_pacakge_id,str) is False:
            raise ValueError("package_id is not str")
        
        if "model_name" not in package_info:
            raise ValueError("model_name is not exist in package_info")
        current_model_name = package_info["model_name"]
        if isinstance(current_model_name,str) is False:
            raise ValueError("current_model_name is not str")
        
        if "model_version" not in package_info:
            raise ValueError("model_version is not exist in package_info")
        current_model_version = package_info["model_version"]
        if isinstance(current_model_version,str) is False:
            raise ValueError("current_model_version is not str")
        
        if isinstance(target_model_name,str) is False:
            raise ValueError("target_model_name is not str")
        if isinstance(target_model_version,str) is False:
            raise ValueError("target_model_version is not str")
        
        self.__model_tool.valid_model_name_and_version(target_model_name,target_model_version)
        self.__model_tool.valid_model_name_and_version(current_model_name,current_model_version)
        
        if current_model_name != target_model_name:
            self.__logger.debug(f'current_model_name {current_model_name} not equal  current_model_version {current_model_version}')
            return
        
        if current_model_version  != target_model_version:
            self.__logger.debug(f'current_model_version {current_model_version} not equal target_model_version {target_model_version}')
            return
        
        main_language = package_info["main_language"]
        schema_class = f'{current_model_name}_{current_model_version}_{main_language}'
        schema_class = self.make_class_name_valid_name(schema_class)
        self.__logger.debug(f'schema_class {schema_class}')
        
        url_to_article_dict,url_to_embedding_dict = self.__model_tool.download_increment_package(target_model_name,target_model_version,current_pacakge_id)
        self.__logger.debug(f'article length= {len(url_to_article_dict)}')
        url_to_success_info = dict()
        self.init_class(current_model_name,current_model_version)
        
        with self.__client.batch(batch_size=100) as batch:
            for current_url, current_article in url_to_article_dict.items():
                current_feed_id = current_article['feed_id']
                # self.__logger.debug(f'current_feed_id {current_feed_id}')
                if black_feed_set is not None:
                
                    if int(current_article['feed_id']) in black_feed_set:
                        # cloud_id = current_article['cloud_id']
                        # current_feed_id = current_article['feed_id']
                        # self.__logger.debug(f'cloud_id cloud_id: {cloud_id}current_feed_id: {current_feed_id} filtered')
                        continue
                url_to_success_info[current_url] = {}
                url_to_success_info[current_url]["success"] = True
                url_to_success_info[current_url]["fail_reasons"] = list()
                temp_property = dict()
                if 'published_at' in current_article and current_article['published_at'] is not None :
                    current_published_at = int(current_article["published_at"])
                    temp_property["published_at"] = current_published_at
                temp_property['cloud_id'] = int(current_article['cloud_id'])

                current_category_name = self.__feed_id_to_feed[int(current_article["feed_id"])]["category_title"]
                current_category_info =  self.__category_name_to_category[current_category_name]
                
                if current_category_info["level"] == "first":
                    temp_property["first_level_category"] = int(current_category_info["id"])
                elif current_category_info["level"] == "second":
                    temp_property["first_level_category"] = int(self.__category_name_to_category[current_category_info["parent"]]["id"])
                
                if "feed_id" in current_article and current_article["feed_id"] is not None:
                    temp_property["feed_id"] = int(current_article["feed_id"])
                    
                
                if current_url not in url_to_embedding_dict:
                    self.__logger.debug(f'current_url {current_url} have no embedding ')
                    continue
                current_embedding_info = url_to_embedding_dict[current_url]
                if metadata is True:
                    summary_temp_property = temp_property.copy()
                    summary_temp_property["subdoc_index"] = -1

                summary_uuid = self.generate_deterministic_id_according_url(f'{current_url}_{-1}')
                url_to_success_info[current_url]["cloud_id"] = int(current_article["cloud_id"])
                url_to_success_info[current_url]["uuids"] = dict()

                try:
                    self.__client.batch.add_data_object(
                        data_object = summary_temp_property,
                        class_name=schema_class,
                        uuid=summary_uuid,
                        vector=current_embedding_info["embeddings"]
                    )                
                    url_to_success_info[current_url]["uuids"]["-1"] = summary_uuid
                except Exception as ex:
                    url_to_success_info[current_url]["success"] = False
                    url_to_success_info[current_url]["fail_reasons"].append(f'summary embedding subdoc_index -1 fail {str(ex)}')
                    self.__logger.debug(f'current_url {str(ex)}')
                
                
                if "subdocembeddings"  in current_embedding_info:
                    for current_sub_embedding_info in current_embedding_info["subdocembeddings"]:
                        sub_temp_property = temp_property.copy()
                        current_subdoc_index = current_sub_embedding_info["subdoc_index"]
                        if metadata is True:
                            sub_temp_property["subdoc_index"] = current_subdoc_index

                        sub_uuid = self.generate_deterministic_id_according_url(f'{current_url}_{current_subdoc_index}')
                        
                        try:
                            self.__client.batch.add_data_object(
                                data_object = sub_temp_property,
                                class_name=schema_class,
                                uuid=sub_uuid,
                                vector=current_sub_embedding_info["embeddings"]
                            )
                            url_to_success_info[current_url]["uuids"][str(current_subdoc_index)] = sub_uuid
                        except Exception as ex:
                            url_to_success_info[current_url]["success"] = False
                            url_to_success_info[current_url]["fail_reasons"].append(f'subdoc embedding {current_subdoc_index} fail {str(ex)}')
                            self.__logger.error(f'current_url {str(ex)}')
        overload_delete_uuid_to_cloud_id = dict()
        if overload_delete:
            overload_delete_uuid_to_cloud_id = self.delete_overload_data_according_latest_embedding(current_model_name,current_model_version,capacity,{})         
        return url_to_success_info,overload_delete_uuid_to_cloud_id
     
    def construct_where_filter(self,package_range_list= None,start_time=None,end_time=None,
                               major_language=None,category_list = None,url_list=None,
                               filtered_condition=False,cloud_id_list=None,feed_id_list=None):
        """_summary_
        filter_example where_filter = {
        "operator": "And",
        "operands": [{
                "path": ["wordCount"],
                "operator": "GreaterThan",
                "valueInt": 1000
            }, {
                "path": ["title"],
                "operator": "Like",
                "valueText": "*economy*",
            }]
        }

        Args:
            package_range_list (_type_, optional): _description_. Defaults to None.
            start_time (_type_, optional): _description_. Defaults to None.
            end_time (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        conditions = {
            "operator": "And",
            "operands": []
            
        }
        '''
        if filtered_condition is not None:
            if isinstance(filtered_condition,bool) is False:
                raise ValueError("filtered_condition is not bool")
            filtered_condition = {
                "path":["filtered"],
                "operator": "Equal",
                "valueBoolean": filtered_condition
            }
            conditions["operands"].append(filtered_condition)
        
        if package_range_list is not None:
            if isinstance(package_range_list,list) is False:
                raise ValueError("package_range_list is not list") 
            if len(package_range_list) >= 1:
                for current_package in package_range_list:
                    if isinstance(current_package,str) is False:
                        raise ValueError("current_package is not str")
                package_condion = {
                        "operator": "Or",
                        "operands": []
                }
                for current_package_id in package_range_list:
                    current_package_condition = {
                        "path": ["package_id"],
                        "operator": "Equal",
                        "valueText": current_package_id
                    }
                    package_condion["operands"].append(current_package_condition)
                conditions["operands"].append(package_condion)
        
        '''
        if start_time is not None:
            if isinstance(start_time,datetime) is False:
                raise ValueError("start_time is not datetime")
            int_start_time = int(start_time.timestamp() * 1000)
            current_start_time_condition = {
                        "path": ["published_at"],
                        "operator": "GreaterThanEqual",
                        "valueInt": int_start_time
            }
            conditions["operands"].append(current_start_time_condition)
            
        if end_time is not None:
            if isinstance(end_time,datetime) is False:
                raise ValueError("end_time is not datetime")
            int_end_time = int(end_time.timestamp() * 1000)
            current_end_time_condition = {
                        "path": ["published_at"],
                        "operator": "LessThanEqual",
                        "valueInt": int_end_time
            }
            conditions["operands"].append(current_end_time_condition)
        
        '''
        if major_language is not None:
            if isinstance(major_language,RecommendSupportLanguageEnum) is False:
                raise ValueError("major_language is not RecommendSupportLanguageEnum")
            str_recommend_language = RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT.get_langdetect_language_according_recommend_support_language(major_language)
            current_language_condition = {
                        "path": ["major_language"],
                        "operator": "Equal",
                        "valueText": str_recommend_language
            }
            conditions["operands"].append(current_language_condition)
        '''

        if category_list is not None:
            if isinstance(category_list,list) is False:
                raise ValueError("keyword_list is not list")
            for current_category in category_list:
                if isinstance(current_category,str) is False:
                    raise ValueError("current_keyword is not str")
                if current_category not in self.__category_name_to_category:
                    raise ValueError("category_name is not valid category_name")
                
            if len(category_list)>0:
                category_condition = {
                        "operator": "Or",
                        "operands": []
                }
                for current_category in category_list:
                    current_category_info = self.__category_name_to_category[current_category]
                    category_level = current_category_info["level"]
                    if category_level == "first":
                        category_field_path = "first_level_category"
                    else:
                        continue
                    # elif category_level == "second":
                    #    category_field_path = "second_level_category"
                    
                    current_category_condition = {
                        "path": category_field_path,
                        "operator": "Equal",
                        "valueInt": int(current_category_info["id"])
                    }
                    category_condition["operands"].append(current_category_condition)
                    
                if len(category_condition["operands"]) > 0:
                    conditions["operands"].append(category_condition)
        ''' 
        if url_list != None:
            if isinstance(url_list,list) is False:
                raise ValueError("url_list is not list")
            for current_url in url_list:
                if isinstance(current_url,str) is False:
                    raise ValueError("current_url is not str")
                
            if len(url_list) > 0:
                url_conditions = {
                        "operator": "Or",
                        "operands": []
                }
                for current_url in url_list:
                    current_url_condition = {
                        "path": "url",
                        "operator": "Equal",
                        "valueText": current_url
                    }
                    url_conditions["operands"].append(current_url_condition)
                conditions["operands"].append(url_conditions)
        '''    
        
        
        if cloud_id_list is not  None:
            if isinstance(cloud_id_list,list) is False:
                raise ValueError("cloud_id_list is not list")
            for current_cloud_id in cloud_id_list:
                if isinstance(current_cloud_id,int) is False:
                    raise ValueError("current_cloud_id is not in")
                
            if len(cloud_id_list) > 0:
                cloud_id_conditions = {
                        "operator": "Or",
                        "operands": []
                }
                for current_cloud_id in cloud_id_list:
                    # self.__logger.debug(f'current_cloud_id {current_cloud_id}')
                    current_cloud_id_condition = {
                        "path": "cloud_id",
                        "operator": "Equal",
                        "valueInt": current_cloud_id
                    }
                    cloud_id_conditions["operands"].append(current_cloud_id_condition)
                conditions["operands"].append(cloud_id_conditions) 
        
        if feed_id_list is not None:
            if isinstance(feed_id_list,list) is False:
                raise ValueError("feed_id_list is not list")
            for current_feed_id in feed_id_list:
                if isinstance(current_feed_id,int) is False:
                    raise ValueError("current_feed_id is not int")
            if len(feed_id_list) > 0:
                feed_id_conditions= {
                     "operator": "Or",
                     "operands":[]
                }
                for current_feed_id in feed_id_list:
                    current_feed_id_condition = {
                        "path":"feed_id",
                        "operator":"Equal",
                        "valueInt":current_feed_id
                    }
                    feed_id_conditions["operands"].append(current_feed_id_condition)
                conditions["operands"].append(feed_id_conditions)
        
        return conditions
         
           
    def search_nearest(self,model_name,model_version,limit,major_language,embedding=None,
                       package_range_list=None,start_time=None,end_time=None,
                       category_list=None,url_list=None,filtered_condition=False,cloud_id_list=None,feed_id_list=None,fetch_vector=False):
        """_summary_
        package_range_list,url_list,filtered_condition not support
        Args:
            model_name (_type_): _description_
            model_version (_type_): _description_
            limit (_type_): _description_
            embedding (_type_, optional): _description_. Defaults to None.
            package_range_list (_type_, optional): _description_. Defaults to None.
            start_time (_type_, optional): _description_. Defaults to None.
            end_time (_type_, optional): _description_. Defaults to None.
            major_language (_type_, optional): _description_. Defaults to None.
            category_list (_type_, optional): _description_. Defaults to None.
            url_list (_type_, optional): _description_. Defaults to None.
            filtered_condition (bool, optional): _description_. Defaults to False.

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_

        Returns:
            _type_: _description_
            when embedding is not None, the distance and certainty is not None
            [{'subdoc_index': -1, 'url': 'https://www.stereogum.com/2231005/samantha-urbani-one-day-at-a-time/music/', 'uuid': '938b5940-c5e1-5571-848a-69e2b3b41d32', 'distance': None, 'certainty': None}, 
            {'subdoc_index': -1, 'url': 'https://projectswordtoys.blogspot.com/2023/07/cabinet-meeting.html', 'uuid': '3023bc5a-59c2-5587-9864-e5925b4dba3d', 'distance': None, 'certainty': None}]
        """
        embedding_dim = self.__model_tool.valid_model_name_and_version(model_name,model_version)["embedding_dim"]
        self.__model_tool.valid_model_name_and_version(model_name,model_version)
        if embedding is not None:
            if isinstance(embedding,list) is False:
                raise ValueError("embedding is not list")
            # self.__logger.debug(embedding)
            if len(embedding) != embedding_dim:
                raise ValueError(f"current_embedding's dim {len(embedding)} is not equal model's embedding_dim {embedding_dim}")
            for current_value in embedding:
                if isinstance(current_value,float) is False:
                    raise ValueError("current_value is not float")
        if isinstance(limit,int) is False:
            raise ValueError("limit is not number")

        if isinstance(major_language,RecommendSupportLanguageEnum) is False:
            raise ValueError("major_language is not RecommendSupportLanguageEnum")
        str_recommend_language = RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT.get_langdetect_language_according_recommend_support_language(major_language)
            
        schema_class = f'{model_name}_{model_version}_{str_recommend_language}'
        capital_schema_class = self.make_class_name_valid_name(schema_class)
        where_filter = self.construct_where_filter(package_range_list=package_range_list,start_time=start_time,end_time=end_time,
                                                   major_language=major_language,category_list=category_list,url_list=url_list,
                                                   filtered_condition=filtered_condition,cloud_id_list=cloud_id_list,feed_id_list=feed_id_list)
        self.__logger.debug(f'capital_schema_class {capital_schema_class} filter {where_filter}')
        additional_properties = ["id","distance","certainty"]
        if fetch_vector:
            additional_properties.append("vector")
        # self.__logger.debug(f'embedding {embedding}')
        if embedding is None:
            if len(where_filter['operands']) > 0:
                response = (
                    self.__client.query
                    .get(capital_schema_class, ["cloud_id","subdoc_index"])
                    .with_additional(additional_properties) # https://weaviate.io/developers/weaviate/config-refs/distances metrics
                    .with_where(where_filter)
                    .with_limit(limit)
                    .do()
                )
                self.__logger.debug(f'filtered condtions exist,embedding not exist')
            else:
                response = (
                    self.__client.query
                    .get(capital_schema_class, ["cloud_id","subdoc_index"])
                    .with_additional(additional_properties) # https://weaviate.io/developers/weaviate/config-refs/distances metrics
                    .with_limit(limit)
                    .do()
                )
                self.__logger.debug(f'filtered condtions not exist,embedding not exist')
        else:
            if len(where_filter['operands']) > 0:
                response = (
                    self.__client.query
                    .get(capital_schema_class, ["cloud_id","subdoc_index"])
                    .with_near_vector({"vector":embedding})
                    .with_additional(additional_properties) # https://weaviate.io/developers/weaviate/config-refs/distances metrics
                    .with_where(where_filter)
                    .with_limit(limit)
                    .do()
                )
                self.__logger.debug(f'filtered condtions  exist,embedding  exist')
            else:
                response = (
                    self.__client.query
                    .get(capital_schema_class, ["cloud_id","subdoc_index"])
                    .with_near_vector({"vector":embedding})
                    .with_additional(additional_properties) # https://weaviate.io/developers/weaviate/config-refs/distances metrics
                    .with_limit(limit)
                    .do()
                )
                self.__logger.debug(f'filtered condtions not  exist,  embedding exist')
                
        # self.__logger.debug(f'response {response}')
        
        if "errors" in response:
            self.__logger.error(f'response {response}')
            return []
        # capital_schema_class = self.make_class_name_valid_name(schema_class)
        article_list = response["data"]["Get"][capital_schema_class]
        if article_list is None:
            self.__logger.error(f'there is no valid item for filter {where_filter}')
            return []
        for current_article in article_list:
            # self.__logger.debug(current_article)
            # self.__logger.debug('111111111111111111111111')
            current_article['uuid'] = current_article["_additional"]["id"]
            current_article['distance'] = current_article["_additional"]["distance"]
            current_article['certainty'] = current_article["_additional"]["certainty"]
            if fetch_vector:
                current_article['vector'] = current_article["_additional"]["vector"]
            del current_article["_additional"]
            # self.__logger.debug(current_article)
        return article_list
    
    def make_class_name_valid_name(self,name):
        if isinstance(name,str) is False:
            raise ValueError("name is not str")
        name = name[0].upper() + name[1:]
        name = name.replace('-','_')
        return name
         
    '''
    def select_same_package_id(self,model_name,model_version,package_id):
        self.__model_tool.valid_model_name_and_version(model_name,model_version)
        if isinstance(package_id,str) is False:
            raise ValueError("package_id is not str")
        schema_class = f'{model_name}_{model_version}'
        where_filter = {
        "path": ["package_id"],
        "operator": "Equal",
        "valueText": package_id
        }
        response = (
            self.__client.query
            .get(schema_class, ["url","subdoc_index"])
            .with_additional(["id","distance"])
            .with_where(where_filter)
            .with_limit(1000)
            .do()
        )
        capital_schema_class = schema_class[0].upper()+schema_class[1:]
        article_list = response["data"]["Get"][capital_schema_class]
        for current_article in article_list:
            current_article['uuid'] = current_article["_additional"]["id"]
            del current_article["_additional"]
        return response["data"]["Get"][capital_schema_class]
    '''
    
    def generate_deterministic_id_according_url(self,url):
        if isinstance(url,str) is False:
            raise ValueError("url is not str")
        str_uuid = generate_uuid5(url)
        return str_uuid
    
    
    def delete_batch_data(self,model_name,model_version,major_language,package_range_list=None,
                          start_time=None,end_time=None,category_list=None,
                          url_list=None,filtered_condition=False,cloud_id_list=None,feed_id_list=None):
        """_summary_
        package_range_list,url_list,filtered_condition not support
        '''
            {
                "dryRun": false,
                "match": {
                    "class": "Dataset",
                    "where": {
                        "operands": null,
                        "operator": "Equal",
                        "path": [
                            "description"
                        ],
                        "valueText": "weather"
                    }
                },
                "output": "verbose",
                "results": {
                    "failed": 0,
                    "limit": 10000,
                    "matches": 2,
                    "objects": [
                        {
                            "id": "1eb28f69-c66e-5411-bad4-4e14412b65cd",
                            "status": "SUCCESS"
                        },
                        {
                            "id": "da217bdd-4c7c-5568-9576-ebefe17688ba",
                            "status": "SUCCESS"
                        }
                    ],
                    "successful": 2
                }
            }
        '''
 

        Args:
            model_name (_type_): _description_
            model_version (_type_): _description_
            dry_run (bool, optional): _description_. Defaults to False.
            package_range_list (_type_, optional): _description_. Defaults to None.
            start_time (_type_, optional): _description_. Defaults to None.
            end_time (_type_, optional): _description_. Defaults to None.
            major_language (_type_, optional): _description_. Defaults to None.
            category_list (_type_, optional): _description_. Defaults to None.
            url_list (_type_, optional): _description_. Defaults to None.
            filtered_condition (bool, optional): _description_. Defaults to False.

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
            {
                "cloud_id":{
                    "success": True,
                    "fail_reason": str
                }
            }
        """
        # if isinstance(dry_run,bool) is False:
        #    raise ValueError("dry_run is not bool")
        if isinstance(major_language,RecommendSupportLanguageEnum) is False:
            raise ValueError("major_language is not RecommendSupportLanguageEnum")
        str_recommend_language = RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT.get_langdetect_language_according_recommend_support_language(major_language)
        self.__client.batch.consistency_level = weaviate.data.replication.ConsistencyLevel.ALL  # default QUORUM
        schema_class = f'{model_name}_{model_version}_{str_recommend_language}'
        capital_schema_class = self.make_class_name_valid_name(schema_class)
        cloud_id_to_success = dict()
        while True:
            item_list = self.search_nearest(model_name,model_version,1000,major_language=RecommendSupportLanguageEnum.ENGLISH,
                                package_range_list=package_range_list,start_time=start_time,end_time=end_time,
                                category_list=category_list,url_list=url_list,filtered_condition=filtered_condition,
                                cloud_id_list=cloud_id_list,feed_id_list=feed_id_list)
            if len(item_list) < 1:
                break
            for current_item in tqdm(item_list,desc=f"delete current select item {capital_schema_class}"):
                cloud_id_to_success[str(current_item["cloud_id"])] = dict()
                try:
                    delete_response = self.__client.data_object.delete(
                        uuid=current_item['uuid'],
                        class_name=capital_schema_class,  # Class of the object to be deleted
                    )
                    # self.__logger.debug(f'delete response {delete_response}')
                    cloud_id_to_success[str(current_item["cloud_id"])]["success"] = True
                except Exception as ex:
                    self.__logger.error(f'error exception: {str(ex)} ')
                    cloud_id_to_success[str(current_item["cloud_id"])]["success"] = False
                    cloud_id_to_success[str(current_item["cloud_id"])]["fail_reason"] = str(ex)
                    
        return cloud_id_to_success     
        
        '''
        if isinstance(major_language,RecommendSupportLanguageEnum) is False:
            raise ValueError("major_language is not RecommendSupportLanguageEnum")
        str_recommend_language = RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT.get_langdetect_language_according_recommend_support_language(major_language)
        
        self.__client.batch.consistency_level = weaviate.data.replication.ConsistencyLevel.ALL  # default QUORUM
        schema_class = f'{model_name}_{model_version}_{str_recommend_language}'
        capital_schema_class = self.make_class_name_valid_name(schema_class)
        # self.__logger.debug(f'delete batch data in {capital_schema_class} class {cloud_id_list}')
        
        where_filter = self.construct_where_filter(package_range_list=package_range_list,start_time=start_time,end_time=end_time,
                                                   major_language=major_language,category_list=category_list,url_list=url_list,
                                                   filtered_condition=filtered_condition)
        count = 1
        summary_result_url_to_success_info = {
            
        }
        self.__logger.debug(f'delete filter {where_filter}')
        while True:
            self.__logger.debug(f'delete filter {where_filter}')
            dry_run_delete_response = self.__client.batch.delete_objects(
                class_name=capital_schema_class,
                # same where operator as in the GraphQL API
                where=where_filter,
                output="verbose",
                dry_run=True,
            )
            matches = dry_run_delete_response["results"]["matches"]
            if matches == 0:
                break
            self.__logger.debug(f"loop delete count {count}")
            count = count + 1
            uuid_set = set()
            for current_object in dry_run_delete_response["results"]["objects"]:
                uuid_set.add(current_object["id"])
                
            uuid_to_cloud_id_dict = dict()
            self.__logger.debug(f"uuid_set {len(uuid_set)}")
            for current_uuid in tqdm(uuid_set):
                current_data_object = self.__client.data_object.get_by_id(
                    current_uuid,
                    class_name=capital_schema_class,
                )
                
                uuid_to_cloud_id_dict[current_uuid] ={
                    "cloud_id":current_data_object["properties"]["cloud_id"],
                    "subdoc_index":current_data_object["properties"]["subdoc_index"]
                }
                
            real_delete_response = self.__client.batch.delete_objects(
                class_name=capital_schema_class,
                # same where operator as in the GraphQL API
                where=where_filter,
                output="verbose",
                dry_run=False,
            )
            for current_object in real_delete_response["results"]["objects"]:
                current_uuid = current_object["id"]
                # self.__logger.debug(current_object["status"])
                if current_object["status"] == "SUCCESS":
                    summary_result_url_to_success_info[uuid_to_cloud_id_dict[current_uuid]["cloud_id"]] = {
                        "success":True
                    }
                else:
                    summary_result_url_to_success_info[uuid_to_cloud_id_dict[current_uuid]["cloud_id"]] = {
                        "success":False
                    }                 
                    
        return  summary_result_url_to_success_info
        '''
    
    '''
    def mark_data_whether_read_according_url(self,model_name,model_version,url_list,whehter_read=False):
        self.__model_tool.valid_model_name_and_version(model_name,model_version)
        if isinstance(url_list,list) is False:
            raise ValueError("url_list is not list")
        if isinstance(whehter_read,bool) is False:
            raise ValueError("whether_read is not bool")
        current_article_list = self.search_nearest(model_name,model_version,limit=len(url_list),url_list=url_list,filtered_condition=None)
        url_to_mark_success = dict()
        schema_class = f'{model_name}_{model_version}'
        for current_article in current_article_list:
            try:
                self.__client.data_object.update(
                    {"filtered":whehter_read},
                    class_name=schema_class,
                    uuid=current_article["uuid"],
                    consistency_level=weaviate.data.replication.ConsistencyLevel.ALL,  # default QUORUM
                )
                url_to_mark_success[current_article["url"]] = {
                    "success":True
                }
            except Exception as ex:
                self.__logger.debug(str(ex))
                url_to_mark_success[current_article["url"]] = {
                    "success":False,
                    "fail_reason":str(ex)
                }
        
        
        for current_url in url_list:
            if current_url not in url_to_mark_success:
                url_to_mark_success[current_url] = {
                    "success": False,
                    "fail_reason":"not exist weaviate"
                }
        return url_to_mark_success
    '''
    
    def get_all_class(self):
        response = self.__client.schema.get()
        class_set = set()
        for current_class_info in response["classes"]:
            class_set.add(current_class_info["class"])
        return class_set
    
    def get_class_according_model_and_version(self,model_name,model_version):
        self.__model_tool.valid_model_name_and_version(model_name,model_version)
        class_name_set = set()
        for current_language in self.__support_language_set:
            class_name = f'{model_name}_{model_version}_{current_language}'
            class_name = self.make_class_name_valid_name(class_name)
            class_name_set.add(class_name)
        return class_name_set
    
    def delete_overload_data_according_latest_embedding(self,model_name,model_version,capacity,language_to_candidate_news_id_to_embedding):
        self.__model_tool.valid_model_name_and_version(model_name,model_version)
        embedding_dim = self.__model_tool.valid_model_name_and_version(model_name,model_version)["embedding_dim"]
        if isinstance(capacity,int) is False:
            raise ValueError("capacity is not int")
        if capacity < 10000:
            capacity = 10000
        if isinstance(language_to_candidate_news_id_to_embedding,dict) is False:
            raise ValueError("language_to_candidate_news_id_to_embedding is not dict")
        
        current_model_class_name_to_candidate_news_id_to_embedding = dict()
        
        current_model_class_name_to_support_language = dict()
        for current_language,candidate_news_id_to_embedding in language_to_candidate_news_id_to_embedding.items():
            lang_detect_language = RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT.get_langdetect_language_according_recommend_support_language(current_language)
            self.__recommend_common_tool.validate_candidate_document_id_to_item_for_weaviate(candidate_news_id_to_embedding,embedding_dim)
            current_class_name = f'{model_name}_{model_version}_{lang_detect_language}'
            current_class_name = self.make_class_name_valid_name(current_class_name)
            current_model_class_name_to_candidate_news_id_to_embedding[current_class_name] = candidate_news_id_to_embedding
            current_model_class_name_to_support_language[current_class_name] = current_language
        
            
        all_class_name_set = self.get_all_class()
        current_model_and_version_class_name_set = self.get_class_according_model_and_version(model_name,model_version)
        for current_class_name in all_class_name_set:
            if current_class_name not in current_model_and_version_class_name_set:
                self.delete_class_according_class_name(current_class_name)
                self.__logger.debug(f'delete {current_class_name} success')
                
        for current_class_name in current_model_and_version_class_name_set:
            if current_class_name not in all_class_name_set:
                self.init_class_according_specific_class_name(current_class_name)
                self.__logger.debug(f'init {current_class_name} success')
                
        class_name_to_count = dict()
        total_count = 0
        for current_class_name in current_model_and_version_class_name_set:
            count = self.get_number_of_one_class(current_class_name)
            class_name_to_count[current_class_name] = count
            total_count = total_count + count
        
        self.__logger.debug(f'{model_name} {model_version} total_count {total_count}')
        if total_count <= capacity:
            self.__logger.debug(f'total {model_name} {model_version} count is small than capacity')
            return
        
        delete_uuid_to_cloud_id = dict()
        for current_class_name,current_count in class_name_to_count.items():
            current_class_number_to_be_delete = current_count - int(capacity * (current_count*1.0/total_count))
            self.__logger.debug(f"class {current_class_name} to be delete {current_class_number_to_be_delete}")
            if current_class_number_to_be_delete > 0:
                if current_class_name not in current_model_class_name_to_candidate_news_id_to_embedding:
                    # delete according 
                    uuid_published_at_cloud_id_tuple_list = self.get_sort_uuid_and_published_at_and_cloud_id_tuple_of_one_class(current_class_name)
                    if len(uuid_published_at_cloud_id_tuple_list) > current_class_number_to_be_delete:
                        uuid_published_at_cloud_id_tuple_list = uuid_published_at_cloud_id_tuple_list[:current_class_number_to_be_delete]
                    for current_tuple in tqdm(uuid_published_at_cloud_id_tuple_list,desc=f"delete record {current_class_name} according published_at"):
                        self.__client.data_object.delete(
                            uuid=current_tuple[0],
                            class_name=current_class_name,  # Class of the object to be deleted
                        )
                        delete_uuid_to_cloud_id[current_tuple[0]] = current_tuple[2]
                else:
                    current_candidate_news_id_to_embedding = current_model_class_name_to_candidate_news_id_to_embedding[current_class_name]
                    current_user_embedding = self.get_user_vector(current_candidate_news_id_to_embedding,50)
                    current_language = current_model_class_name_to_support_language[current_class_name] 
                    item_list = self.search_nearest(model_name,model_version,current_class_number_to_be_delete,
                                        major_language=current_language,embedding=current_user_embedding*(-1))
                    for current_item in tqdm(item_list,desc=f"delete record {current_class_name} according farthest"):
                        self.__client.data_object.delete(
                            uuid=current_item["id"],
                            class_name=current_class_name,  # Class of the object to be deleted
                        )
                        delete_uuid_to_cloud_id[current_tuple[0]] = current_tuple[2]
        return delete_uuid_to_cloud_id
        
        # find least similar results 
        
        
            
    
    def __get_batch_with_cursor(self, class_name, cursor=None):
        query = (
            self.__client.query.get(class_name, ['cloud_id','published_at'])
            # Optionally retrieve the vector embedding by adding `vector` to the _additional fields
            .with_additional(["id"])
            .with_limit(1000)
        )
        if cursor is not None:
            return query.with_after(cursor).do()
        else:
            return query.do()
    
    def get_number_of_one_class(self,class_name):
        class_name_set = self.get_all_class()
        if class_name not in class_name_set:
            raise ValueError("class_name is not exist")
        result = self.__client.query.aggregate(class_name).with_meta_count().do()
        # {'data': {'Aggregate': {'Bert_v2_en': [{'meta': {'count': 10098}}]}}}
        count = result["data"]["Aggregate"][class_name][0]["meta"]["count"]
        return count
 
    def get_uuid_to_cloud_id_dict_of_one_class(self,class_name):
        if isinstance(class_name,str) is False:
            raise ValueError("class_name is not str")
        all_class_name_set = self.get_all_class()
        if class_name not in all_class_name_set:
            raise ValueError("class_name is not in weaviate")
        cursor = None
        total_count = 0
        uuid_id_to_cloud_id = dict()
        while True:
            current_response = self.__get_batch_with_cursor(class_name, cursor)
            item_list = current_response["data"]["Get"][class_name]
            if len(item_list) == 0:
                break
            cursor = item_list[-1]["_additional"]["id"]
            for current_item in item_list:
                uuid_id_to_cloud_id[current_item["_additional"]["id"]] = current_item["cloud_id"]
            total_count = total_count + len(item_list)
        # self.__logger.debug(results)
        return uuid_id_to_cloud_id
    
    def get_uuid_to_published_at_dict_of_one_class(self,class_name):
        if isinstance(class_name,str) is False:
            raise ValueError("class_name is not str")
        all_class_name_set = self.get_all_class()
        if class_name not in all_class_name_set:
            raise ValueError("class_name is not in weaviate")
        cursor = None
        total_count = 0
        uuid_id_to_published_at = dict()
        while True:
            current_response = self.__get_batch_with_cursor(class_name, cursor)
            item_list = current_response["data"]["Get"][class_name]
            if len(item_list) == 0:
                break
            cursor = item_list[-1]["_additional"]["id"]
            for current_item in item_list:
                uuid_id_to_published_at[current_item["_additional"]["id"]] = current_item["published_at"]
            total_count = total_count + len(item_list)
        # self.__logger.debug(results)
        return uuid_id_to_published_at
    
    def get_uuid_to_article_info_of_one_class(self,class_name):
        if isinstance(class_name,str) is False:
            raise ValueError("class_name is not str")
        all_class_name_set = self.get_all_class()
        if class_name not in all_class_name_set:
            raise ValueError("class_name is not in weaviate")
        cursor = None
        total_count = 0
        uuid_id_to_article_info = dict()
        while True:
            current_response = self.__get_batch_with_cursor(class_name, cursor)
            item_list = current_response["data"]["Get"][class_name]
            if len(item_list) == 0:
                break
            cursor = item_list[-1]["_additional"]["id"]
            for current_item in item_list:
                uuid_id_to_article_info[current_item["_additional"]["id"]] = {
                    "published_at":current_item["published_at"],
                    "cloud_id":current_item["cloud_id"]
                }

            total_count = total_count + len(item_list)
        # self.__logger.debug(results)
        return uuid_id_to_article_info
    
    def get_sort_uuid_and_published_at_and_cloud_id_tuple_of_one_class(self,class_name):
        uuid_id_to_article_info = self.get_uuid_to_article_info_of_one_class(class_name)
        tuple_list=list()
        none_list = list()
        for current_uuid,current_article_info in uuid_id_to_article_info.items():
            if current_article_info["published_at"] is not None:
                tuple_list.append((current_uuid,current_article_info["published_at"],current_article_info["cloud_id"]))
            else:
                none_list.append((current_uuid,current_article_info["published_at"],current_article_info["cloud_id"]))
        
        none_list.extend(tuple_list)
        return none_list

    def get_user_vector(self,candidate_news_id_to_embedding,num_clicked_news_a_user=50):
        current_list_embedding = list()
        for current_id, current_embedding_info in candidate_news_id_to_embedding.items():
            current_list_embedding.append(current_embedding_info['embedding'])
        if len(current_list_embedding) > num_clicked_news_a_user:
            current_list_embedding = current_list_embedding[:num_clicked_news_a_user]
        stack_candidate_embedding = np.stack(current_list_embedding)
        
        user_embedding = stack_candidate_embedding.sum(axis=0,keepdims=True)
        return user_embedding
    
    def insert_list_article_embedding(self,model_name, model_version, url_to_article_embedding_info):
        """_summary_
        Args:
            url_to_subdoc_to_article_embedding_info (_type_): _description_
            {
                "url":{
                    "cloud_id":
                    "published_at:
                    "first_level_category"
                    "embeddings":{
                        "subdoc_index":[]
                    }
                }
            }
        """
        embedding_dim = self.__model_tool.valid_model_name_and_version(model_name,model_version)["embedding_dim"]
        if isinstance(url_to_article_embedding_info,dict) is False:
            raise ValueError("url_to_article_embedding_info is not dict")
        for current_url, article_embedding_info in url_to_article_embedding_info.items():
            if isinstance(current_url,str) is False:
                raise ValueError("current_url is not str")
            if isinstance(article_embedding_info,dict) is False:
                raise ValueError("article_embedding_info is not dict")
            if "published_at" not in article_embedding_info:
                raise ValueError("published_at is not exist")
            current_published_at = article_embedding_info["published_at"]
            if isinstance(current_published_at,datetime) is False:
                raise ValueError("current_published_at is not datetime")
            
            if "cloud_id" not in article_embedding_info:
                raise ValueError("cloud_id is not in article_embedding_info")
            current_cloud_id = article_embedding_info["cloud_id"]
            if isinstance(current_cloud_id,int) is False:
                raise ValueError("current_cloud_id is not int")
            
            if "embeddings" not in article_embedding_info:
                raise ValueError("embeddings not exist")
            subdoc_index_to_embedding = article_embedding_info["embeddings"]
            for current_subdoc_index,current_embedding in subdoc_index_to_embedding.items():
                if isinstance(current_subdoc_index,int) is False:
                    raise ValueError("current_subdoc_index is not int")
                if isinstance(current_embedding,list) is False:
                    raise ValueError("current_embedding is not list")
                if len(current_embedding) != embedding_dim:
                    raise ValueError(f"current_embedding dim is not equal {embedding_dim}")
                for current_value in current_embedding:
                    if isinstance(current_value,float) is False:
                        raise ValueError(f"{current_url}  {current_subdoc_index} embeeding  value is not float")
                
            
            if "first_level_category" in article_embedding_info:
                current_first_level_category_name = article_embedding_info["first_level_category"]
                if isinstance(current_first_level_category_name,str) is False:
                    raise ValueError("current_first_level_category_name is not sr")
                if current_first_level_category_name  not in self.__category_name_to_category:
                    raise ValueError("current_first_level_category_name is not valid")
                current_category_info = self.__category_name_to_category[current_first_level_category_name]
                if current_category_info["parent_id"] != 0:
                    raise ValueError("current_first_level_category_name is not first level")

            
        with self.__client.batch(batch_size=100) as batch:
            for current_url, article_embedding_info in url_to_article_embedding_info.items():
                current_published_at = article_embedding_info["published_at"]
                current_cloud_id = article_embedding_info["cloud_id"]
                current_category_id = None
                if "first_level_category" in article_embedding_info:
                    current_first_level_category_name = article_embedding_info["first_level_category"]
                    current_category_id = self.__category_name_to_category[current_first_level_category_name]["id"]
                subdoc_index_to_embedding = article_embedding_info["embeddings"]
                for current_subdoc_index, current_embedding in subdoc_index_to_embedding.items():
                    temp_property=dict()
                    temp_property["cloud_id"] = current_cloud_id
                    
    def delete_all_data(self):
        """_summary_

        Returns:
            _type_: _description_ true delete success
        
        """
        result = True
        try:
            class_name_set = self.get_all_class()
            for current_class_name in class_name_set:
                self.delete_class_according_class_name(current_class_name)
        except Exception as ex:
            self.__logger.debug(f'delete exception {str(ex)}')
            result = False
        return result
    
    def get_total_count_data_weaviate(self):
        class_name_set = self.get_all_class()
        total_count = 0
        for current_class_name in class_name_set:
            current_count = self.get_number_of_one_class(current_class_name)
            total_count = total_count + current_count
        return total_count
        
        