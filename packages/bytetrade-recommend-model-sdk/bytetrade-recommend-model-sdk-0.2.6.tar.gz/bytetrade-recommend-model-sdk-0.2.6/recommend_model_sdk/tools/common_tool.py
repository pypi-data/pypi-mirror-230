from collections.abc import Iterable
from datetime import datetime
import itertools
import gzip
import hashlib
import json
import os
import pandas as pd
import shutil


class CommonTool:
    def __init__(self) -> None:
        self.__language_set = set(['english'])
        model_management_file = os.path.join(os.path.join(self.get_project_directory(),"resources"),"model_management.json")
        self.__model_related_files_suffix_set = set(["gz","direct"])
        self.__model_dict = self.validate_model_management_file(model_management_file)

    def read_excel(self,path):
        if isinstance(path,str) is False:
            raise ValueError('path is not str')
        df = pd.read_excel(path)
        return json.loads(df.to_json(orient='records'))
    
    def write_json(self,content,path):
        if isinstance(content,dict) is False:
            raise ValueError("content is not dict")
        if isinstance(path, str) is False:
            raise ValueError("path is not str")
        with open(path, "w") as outfile:
            json.dump(content, outfile)
    
    def read_json(self,path):
        if isinstance(path,str) is False:
            raise ValueError("path is not str")
        if os.path.exists(path) is False:
            raise ValueError('current_path {current_path} is not exist'.format(current_path = path))
        with open(path, 'r', encoding="utf-8") as f:
            data = json.load(f)
        return data
    
    def get_project_directory(self):
        project_root = os.path.dirname(os.path.dirname(__file__))
        return project_root
    
    def get_offset_from_utc_hours(self,time_zone):
        import datetime
        current_time = datetime.datetime.now(time_zone)
        offset_hours = current_time.utcoffset().total_seconds()/60/60
        return offset_hours
    
    def get_logger(self):
        import logging
        logger = logging.getLogger(__name__)
        FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
        logging.basicConfig(format=FORMAT)
        logger.setLevel(logging.DEBUG)
        return logger
    
    def calculate_md5(self,path):
        if isinstance(path,str) is False:
            raise ValueError("path is not str")
        if os.path.exists(path) is False:
            raise ValueError(f'path {path} is not exist')
        with open(path, 'rb') as f:
            digest = hashlib.md5(f.read()).hexdigest()
        return digest
    
    def calculate_md5_for_big_file(self,path,blocksize=2**27):
        if isinstance(path,str) is False:
            raise ValueError("path is not str")
        if os.path.exists(path) is False:
            raise ValueError(f'path {path} is not exist')
        m = hashlib.md5()
        with open( path , "rb" ) as f:
            while True:
                buf = f.read(blocksize)
                if not buf:
                    break
                m.update( buf )
        return m.hexdigest()
    
    def uncompress_file_gzip(self,input_path,output_path):
        if isinstance(input_path,str) is False:
            raise ValueError(f'input_path is not str')
        if os.path.exists(input_path) is False:
            raise ValueError(f'input_path {input_path} is not exist')
        if input_path[len(input_path)-3:] != ".gz":
            raise ValueError(f'not valid gz')
        with gzip.open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out,length=2**20)
    
    
    def compute_diff_time(self,start_time,end_time):
        if isinstance(start_time,datetime) is False:
            raise ValueError('start_time is not datetime')
        if isinstance(end_time,datetime) is False:
            raise ValueError('end_time is not datetime')
        if end_time < start_time:
            raise ValueError('end_time is small than start_time')
        diff = end_time-start_time 
        diff_in_seconds = diff.total_seconds() 
        return diff_in_seconds
    
    def validate_model_key_field(self,current_model_detail):
        '''
        v1":{
            "mongodb_embedding_field":"word2vec_google_v1",
            "pg_embedding_mark_field":"word2vec_google_embedding",
            "s3_bucket":"gpu-model-data",
            "model_related_files":["GoogleNews-vectors-negative300.bin","tfidf.model","dictionary"]
        }
        '''
        if isinstance(current_model_detail,dict) is False:
            raise ValueError('mongodb_embedding_field is not dict')
        if "mongodb_embedding_field" not in current_model_detail:
            raise ValueError("mongodb_embedding_field is not exist")
        mongodb_embedding_field = current_model_detail["mongodb_embedding_field"]
        if isinstance(mongodb_embedding_field,str) is False:
            raise ValueError("mongodb_embedding_field is not exist")
        
        if "pg_embedding_mark_field" not in current_model_detail:
            raise ValueError("pg_embedding_mark_field is not exist")
        pg_embedding_mark_field = current_model_detail["pg_embedding_mark_field"]
        if isinstance(pg_embedding_mark_field,str) is False:
            raise ValueError("pg_embedding_mark_field is not str")
        
        if "s3_bucket" not in current_model_detail:
            raise ValueError("s3_bucket not in")
        s3_bucket = current_model_detail["s3_bucket"]
        if isinstance(s3_bucket,str) is False:
            raise ValueError("s3_bucket is not str")
        
        if "model_related_files" not in  current_model_detail:
            raise ValueError("model_related_files is not exist")
        model_related_files = current_model_detail["model_related_files"]
        if isinstance(model_related_files,list) is False:
            raise ValueError("model_related_files not exist")
        for current_file in model_related_files:
            if isinstance(current_file,str) is False:
                raise ValueError("current_file is not exist")
        
        if "model_related_files_suffix" not in current_model_detail:
            raise ValueError("model_related_files_suffix not in current_model_detail")
        model_related_files_suffix = current_model_detail["model_related_files_suffix"]
        if isinstance(model_related_files_suffix,dict) is False:
            raise ValueError("model_related_files_suffix is not dict")
        for current_file_name in model_related_files:
            if current_file_name not in model_related_files_suffix:
                raise ValueError(f'current_file_name {current_file_name} have no suffix')
            
            current_file_name_suffix = model_related_files_suffix[current_file_name]
            if current_file_name_suffix not in self.__model_related_files_suffix_set:
                raise ValueError(f"current_file_name_suffix {current_file_name_suffix} is not valid")
        
        if "model_related_files_public" not in current_model_detail:
            raise ValueError("model_related_files_public is not exist")
        model_related_files_public = current_model_detail["model_related_files_public"]
        for current_file_name in model_related_files:
            if current_file_name not in model_related_files_public:
                raise ValueError(f"current_file_name {current_file_name} not in model_related_files_public")
            current_file_name_public = model_related_files_public[current_file_name]
            if isinstance(current_file_name_public,bool) is False:
                raise ValueError(F"current_file_name {current_file_name} current_file_name_public is  not bool")


        
    def validate_model_management_file(self,path):
        if isinstance(path,str) is False:
            raise ValueError(f"path {path} is not str")
        if os.path.exists(path) is False:
            raise ValueError(f"model management file {path} is not exist")
        model_management_dict = self.read_json(path)
        model_name_set = model_management_dict.keys()
        
        
        mongodb_embedding_field_set =  set()
        pg_embedding_mark_field_set = set()
        for current_model_name in model_name_set:
            if len(model_management_dict[current_model_name]) < 1:
                raise ValueError(f'current_model {current_model_name} have not valid model')
            for version_name,current_model_detail in model_management_dict[current_model_name].items():
                self.validate_model_key_field(current_model_detail)
                mongodb_embedding_field = current_model_detail["mongodb_embedding_field"]
                pg_embedding_mark_field = current_model_detail["pg_embedding_mark_field"]
                if mongodb_embedding_field in mongodb_embedding_field_set:
                    raise ValueError(f"mongodb_embedding_field {mongodb_embedding_field} exist more than two model version")
                else:
                    mongodb_embedding_field_set.add(mongodb_embedding_field)
                if pg_embedding_mark_field in pg_embedding_mark_field_set:
                    raise ValueError(f"pg_embedding_mark_field {pg_embedding_mark_field} exist more than  model version")
                else:
                    pg_embedding_mark_field_set.add(pg_embedding_mark_field)
        return model_management_dict
    
    
    def valid_model_name_and_version(self,model_name,model_version):
        if isinstance(model_name,str) is False:
            raise ValueError("model name need to be str")
        if isinstance(model_version,str) is False:
            raise ValueError("model_version need to be str")
        
        if model_name not in self.__model_dict:
            raise ValueError(f"model_name {model_name} not exist")
        
        if model_version not in self.__model_dict[model_name]:
            raise ValueError(f'model_version {model_version} not exist')
        
        return self.__model_dict[model_name][model_version]
    
    def calculate_md5_for_set_str(self,set_str):
        if isinstance(set_str,set) is False:
            raise ValueError("set_str is not set")
        
        for current_str in set_str:
            if isinstance(current_str,str) is False:
                raise ValueError("current_str is not str")
        
        list_str = list(set_str)
        list_str.sort()
        
        concat_str = ''
        for current_str in list_str:
            concat_str = concat_str + current_str
        digest = hashlib.md5(concat_str.encode()).hexdigest()
        return digest
    
    def get_default_environment_variable(self):
        default_environment = dict()
        default_environment["model_path"] =  os.environ.get('model_path', "/ssd/code/MODEL_CLIENT")
        default_environment["weaviate_cloud"] = os.environ.get("weaviate_cloud",False)
        default_cloud_weaviate_url = 'https://test-recommend-9b6u510q.weaviate.network'
        default_cloud_weaviate_api_key = 'mxG7eRQWdu1ruLaCixZUdoLaTrkAsuiifTLw'
        default_environment["cloud_weaviate_url"] = os.environ.get('cloud_weaviate_url',default_cloud_weaviate_url)
        default_environment["cloud_weaviate_api_key"] = os.environ.get('cloud_weaviate_api_key',default_cloud_weaviate_api_key)
        default_private_weaviate_ip = "127.0.0.1"
        default_private_weaviate_port = 9000
        default_environment["private_weaviate_ip"] = os.environ.get("private_weaviate_ip",default_private_weaviate_ip)
        default_environment["private_weaviate_port"] = os.environ.get("private_weaviate_port",default_private_weaviate_port)
        return default_environment
    
    def make_combination_parameter(self,parameter_name_to_parameter_value_list):
        if isinstance(parameter_name_to_parameter_value_list,dict) is False:
            raise ValueError("parameter_name_to_parameter_value_list is not list")
        parameter_name_value_tuple_list_lists = list()
        for current_parameter_name,parameter_value_list in parameter_name_to_parameter_value_list.items():
            if isinstance(current_parameter_name,str) is False:
                raise ValueError("current_parameter_name is not str")
            if isinstance(parameter_value_list,list) is False:
                raise ValueError("parameter_value_list is not list")
            current_parameter_name_value_tuple_list = list()
            for current_value in parameter_value_list:
                current_parameter_name_value_tuple_list.append((current_parameter_name,current_value))
            parameter_name_value_tuple_list_lists.append(current_parameter_name_value_tuple_list)
        combination_tuple_list_lists = list(itertools.product(*parameter_name_value_tuple_list_lists))
        dict_list = list()
        for current_combination_tuple_list in combination_tuple_list_lists:
            temp_dict = dict()
            for current_tuple in current_combination_tuple_list:
                temp_dict[current_tuple[0]] = current_tuple[1]
            dict_list.append(temp_dict)
        return dict_list
        
    def valiate_file_path(self,file_path,custom_info=''):
        if isinstance(custom_info,str) is False:
            raise ValueError("custom_info is not str")
        if isinstance(file_path,str) is False:
            raise ValueError(f"{custom_info}  is not str")
        if os.path.exists(file_path) is False:
            raise ValueError(f"{custom_info} {file_path} is not exist")
        if os.path.isfile(file_path) is False:
            raise ValueError(f"{custom_info} {file_path} is not file")
        
    def validate_directory_path(self,directory_path,custom_info=''):
        if isinstance(custom_info,str) is False:
            raise ValueError("custom_info is not str")
        if isinstance(directory_path,str) is False:
            raise ValueError(f"{custom_info}  is not str")
        if os.path.exists(directory_path) is False:
            raise ValueError(f"{custom_info} {directory_path} is not exist")
        if os.path.isdir(directory_path) is False:
            raise ValueError(f"{custom_info} {directory_path} is not directory")
    
    def batch_next(self,iterable_object, batch_size=1):
        if isinstance(iterable_object,Iterable) is False:
            raise ValueError("iterable_object is not Iterable")
        if isinstance(batch_size,int) is False:
            raise ValueError("batch_size is not int")
        if batch_size < 1:
            raise ValueError("batch_size is small than 1")
        total_length = len(iterable_object)
        for ndx in range(0, total_length, batch_size):
            yield iterable_object[ndx:min(ndx + batch_size, total_length)]