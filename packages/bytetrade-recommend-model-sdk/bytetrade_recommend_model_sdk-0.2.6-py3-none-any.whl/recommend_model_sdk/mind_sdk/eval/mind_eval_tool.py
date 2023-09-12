import json
from multiprocessing import Pool
import numpy as np
import os
import sys
import torch
from torch.utils.data import  DataLoader
from tqdm import tqdm


from recommend_model_sdk.mind_sdk.config.mind_base_config import MINDBaseConfig
from recommend_model_sdk.mind_sdk.experiment_enum import DatasetKindEnum
from recommend_model_sdk.mind_sdk.dataset.mind_news_dataset import MINDNewsDataset
from recommend_model_sdk.mind_sdk.dataset.mind_behaviours_dataset import MINDBehaviorsDataset
from recommend_model_sdk.mind_sdk.eval.eval_operation import calculate_single_user_metric
from recommend_model_sdk.tools.aws_s3_tool import AWSS3Tool
from recommend_model_sdk.tools.common_tool import CommonTool





class MindEvalTool:
    def __init__(self) -> None:
        self.__bucket_name = "gpu-model-data"
        self.__aws_tool = AWSS3Tool()
        self.__common_tool = CommonTool()
        self.__logger = self.__common_tool.get_logger()

    
    def get_all_news_id_set(self):
        mind_users_id_key = "mind_users_id_set"
        all_users_id_dict = self.__aws_tool.get_object_dict(self.__bucket_name,mind_users_id_key)['dict']
        
        return all_users_id_dict["users_id"]
    
    def get_user_impression_log_data_according_user_id(self,user_id):
        user_original_data_key =  f'mind_{user_id}_original_impression_log'
        user_orginal_data = self.__aws_tool.get_object_dict(self.__bucket_name,user_original_data_key)['dict']
        '''
        ['impression_id', 'user', 'time', 'clicked_news', 'impressions', 'dataset_kind']
        {
            "impression_id":{
                "impression_id":int,
                "user":str
                "time":str
                "clicked_news":str
                "impressions":
                "dataset_kind":
            }
            186420
        }
        '''
        return user_orginal_data
        
    
    def eval_depreciated(self,recall_method,rank_method):
        all_users_id_set = self.get_all_news_id_set()
        for current_users_id in all_users_id_set:
            train_impression_log_list = list()
            test_impression_log_list = list()
            val_impression_log_list = list()
            current_user_impression_logs_collection = self.get_user_impression_log_data_according_user_id(current_users_id)
            train_news_id_set = set()
            test_news_id_set = set()
            for current_impression_id , current_impression_log_dict in current_user_impression_logs_collection.items():
                if current_impression_log_dict["dataset_kind"] == int(DatasetKindEnum.train):
                    train_impression_log_list.append(current_impression_log_dict)
                elif current_impression_log_dict["dataset_kind"] == int(DatasetKindEnum.test):
                    test_impression_log_list.append(current_impression_log_dict)
                elif current_impression_log_dict["dataset_kind"] == int(DatasetKindEnum.val):
                    val_impression_log_list.append(current_impression_log_dict)
            
            self.__logger.debug(f'samples train {len(train_impression_log_list)} test {len(test_impression_log_list)} val {len(val_impression_log_list)}')
            
            if len(train_impression_log_list) < 1 or len(test_impression_log_list) < 1:
                continue
            
            for current_train_impression_log_dict in train_impression_log_list:
                current_clicked_news = current_train_impression_log_dict["clicked_news"]
                current_impressions = current_train_impression_log_dict["impressions"]
                for current_news_id in current_clicked_news.split():
                    train_news_id_set.add(current_news_id)
                for current_news_impression in current_impressions.split():
                    if current_news_impression.endswith('1'):
                        train_news_id_set.add(current_news_impression[:len(current_news_impression)-2])
            
            for current_test_impression_log in test_impression_log_list:
                pass
    
    def eval_mind(self, model, news_parsed_tsv_path, behaviours_tsv_path,num_workers, config, model_root_dir,override_news_id_to_embedding=False,max_count=sys.maxsize):
        """
        model is 
        Returns:
            AUC
            MRR
            nDCG@5
            nDCG@10
        """
        
        if isinstance(behaviours_tsv_path,str) is False:
            raise ValueError(f"behaviours_tsv_path {behaviours_tsv_path}")
        if os.path.exists(behaviours_tsv_path) is False:
            raise ValueError(f"behaviours_tsv_path {behaviours_tsv_path} is not exist")
        if isinstance(news_parsed_tsv_path,str) is False:
            raise ValueError(f"news_parsed_tsv_path {news_parsed_tsv_path}")
        if os.path.exists(news_parsed_tsv_path) is False:
            raise ValueError(f"news_parsed_tsv_path {news_parsed_tsv_path} is not exist")
        if isinstance(model_root_dir,str) is False:
            raise ValueError(f"model_root_dir {model_root_dir}")
        if os.path.exists(model_root_dir) is False:
            raise ValueError(f"news_parsed_tsvmodel_root_dir_path {model_root_dir} is not exist")      
        if isinstance(config,MINDBaseConfig) is False:
            raise ValueError("config is not ")
        
        collection_news_id_to_embedding_dir = os.path.join(model_root_dir,"collection_news_id_to_embedding")
        if os.path.exists(collection_news_id_to_embedding_dir) is False:
            os.makedirs(collection_news_id_to_embedding_dir)
        
        
        
        # put all news dataset into 
        news_dataset = MINDNewsDataset(news_parsed_tsv_path,config)
        news_dataloader = DataLoader(news_dataset,
                                    batch_size=config.batch_size * 16,
                                    shuffle=False,
                                    num_workers=config.num_workers,
                                    drop_last=False,
                                    pin_memory=True)
        # get all news id list
        all_news_id_set = news_dataset.get_news_id_set()
        all_news_id_hash = self.__common_tool.calculate_md5_for_set_str(all_news_id_set)
        collection_news_id_to_embedding_file_name = f'collection_{config.embedding_model_name}_{config.embedding_model_version}_{all_news_id_hash}.pt'
        collection_news_id_to_embedding_path = os.path.join(collection_news_id_to_embedding_dir,collection_news_id_to_embedding_file_name)
        if  override_news_id_to_embedding is False and  os.path.exists(collection_news_id_to_embedding_path) is True:
            news2vector = torch.load(collection_news_id_to_embedding_path)
            self.__logger.debug(f'news2vector exist')
        else:
            self.__logger.debug(f'news2vector calculationg..')
            news2vector = {}
            for minibatch in tqdm(news_dataloader,
                                desc="Calculating vectors for news"):
                news_ids = minibatch["id"]
                if any(id not in news2vector for id in news_ids):
                    news_vector = model.get_news_vector(minibatch)
                    for id, vector in zip(news_ids, news_vector):
                        if id not in news2vector:
                            news2vector[id] = vector
            # put news2vector into local model directory
            torch.save(news2vector,collection_news_id_to_embedding_path)
        
        
        '''
        news2vector['PADDED_NEWS'] = torch.zeros(
            list(news2vector.values())[0].size())

        user_dataset = MINDUserDataset(behaviours_parse_tsv_path,
                                user_to_int_tsv_path)
        user_dataloader = DataLoader(user_dataset,
                                    batch_size=config.batch_size * 16,
                                    shuffle=False,
                                    num_workers=config.num_workers,
                                    drop_last=False,
                                    pin_memory=True)

        user2vector = {}
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        for minibatch in tqdm(user_dataloader,
                            desc="Calculating vectors for users"):
            user_strings = minibatch["clicked_news_string"]
            if any(user_string not in user2vector for user_string in user_strings):
                clicked_news_vector = torch.stack([
                    torch.stack([news2vector[x].to(device) for x in news_list],
                                dim=0) for news_list in minibatch["clicked_news"]],
                                                dim=0).transpose(0, 1)
   
                user_vector = model.get_user_vector(clicked_news_vector)
                for user, vector in zip(user_strings, user_vector):
                    if user not in user2vector:
                        user2vector[user] = vector
        '''
        
        behaviors_dataset = MINDBehaviorsDataset(behaviours_tsv_path,config)
        behaviors_dataloader = DataLoader(behaviors_dataset,
                                        batch_size=1,
                                        shuffle=False,
                                        num_workers=config.num_workers)

        count = 0

        tasks = []

        for minibatch in tqdm(behaviors_dataloader,
                            desc="Calculating probabilities"):
            count += 1
            if count == max_count:
                break
            
            '''
            candidate_news_vector = torch.stack([
                model.get_single_news_vector(news[0].split('-')[0])
                for news in minibatch['impressions']
            ],dim=0)
            '''
            
            candidate_news_vector = torch.stack([
                news2vector[news[0].split('-')[0]]
                for news in minibatch['impressions']
            ],dim=0)
            
            for news in minibatch['impressions']:
                pass
            
            clicked_news_id_list = minibatch['clicked_news_string'][0].split()
            if len(clicked_news_id_list) < 1:
                continue
            user_vector = model.get_sinle_user_vector(clicked_news_id_list,news2vector)
            click_probability = model.get_prediction(candidate_news_vector,
                                                    user_vector)

            y_pred = click_probability.tolist()
            y_true = [
                int(news[0].split('-')[1]) for news in minibatch['impressions']
            ]

            tasks.append((
                          , y_pred))

        with Pool(processes=num_workers) as pool:
            results = pool.map(# `calculate_single_user_metric` is a function that takes the true
            # labels and predicted probabilities for a single user's impressions
            # and calculates the following metrics:
            calculate_single_user_metric, tasks)

        aucs, mrrs, ndcg5s, ndcg10s = np.array(results).T

        MEAN_AUCS = np.nanmean(aucs), 
        MEAN_MRRS = np.nanmean(mrrs), 
        MEAN_nDCG5S = np.nanmean(ndcg5s), 
        MEAN_nDCG10S = np.nanmean(ndcg10s)
        result = {
            "MEAN_AUCS":MEAN_AUCS,
            "MEAN_MRRS":MEAN_MRRS,
            "MEAN_nDCG5S":MEAN_nDCG5S,
            "MEAN_nDCG10S":MEAN_nDCG10S,
            "model":model.get_model_name(),
            "news_parsed_tsv_path":news_parsed_tsv_path,
            "behaviours_tsv_path":behaviours_tsv_path,            
        }
        return result
            
            
            
            
            
    
    
  