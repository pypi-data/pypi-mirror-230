import json
from multiprocessing import Pool
import numpy as np
import os
import sys
import torch
import torch.nn as nn
from torch.utils.data import  DataLoader
from tqdm import tqdm


from recommend_model_sdk.mind_sdk.config.dnn_click_predictor_config import DNNClickPredictorConfig
from recommend_model_sdk.mind_sdk.experiment_enum import DatasetKindEnum
from recommend_model_sdk.mind_sdk.dataset.mind_news_dataset import MINDNewsDataset
from recommend_model_sdk.mind_sdk.dataset.mind_behaviours_parsed_dataset import MINDBehaviorsParsedDataset
from recommend_model_sdk.mind_sdk.eval.eval_operation import calculate_single_user_metric
from recommend_model_sdk.tools.aws_s3_tool import AWSS3Tool
from recommend_model_sdk.tools.common_tool import CommonTool
from recommend_model_sdk.mind_sdk.model.dnn_click_predictor import DNNClickPredictor
from recommend_model_sdk.mind_sdk.model.content_similar_model import ContentSimilarModel

class MINDDNNClickPredictorTrainTool:
    def __init__(self) -> None:
        self.__common_tool = CommonTool()
        self.__logger = self.__common_tool.get_logger()
    
    def train(self, behaviours_parsed_tsv_path,num_workers, config, experiment_dir,override_all_news_id_and_impression_id=False,override_news_id_to_embedding=False,override_impression_id_to_embedding=False):
        if isinstance(behaviours_parsed_tsv_path,str) is False:
            raise ValueError(f"behaviours_tsv_path {behaviours_parsed_tsv_path}")
        if os.path.exists(behaviours_parsed_tsv_path) is False:
            raise ValueError(f"behaviours_parsed_tsv_path {behaviours_parsed_tsv_path} is not exist")
        if isinstance(experiment_dir,str) is False:
            raise ValueError(f"model_root_dir {experiment_dir}")
        if os.path.exists(experiment_dir) is False:
            raise ValueError(f"news_parsed_tsvmodel_root_dir_path {experiment_dir} is not exist")      
        if isinstance(config,DNNClickPredictorConfig) is False:
            raise ValueError("config is not DNNClickPredictorConfig")
        
        behaviour_dataset = MINDBehaviorsParsedDataset(behaviours_parsed_tsv_path,config)

        
        collection_all_news_id_and_all_impression_id_dir = os.path.join(experiment_dir,'all_news_id_set_and_impression_id_set')
        if os.path.exists(collection_all_news_id_and_all_impression_id_dir) is False:
            os.makedirs(collection_all_news_id_and_all_impression_id_dir)
        collection_all_news_id_and_all_impression_id_path = os.path.join(collection_all_news_id_and_all_impression_id_dir,'all_news_id_set_and_impression_id_set.pt')
        if override_all_news_id_and_impression_id is True or os.path.exists(collection_all_news_id_and_all_impression_id_path) is False:
            self.__logger.debug('all_news_id_set_and_impression_id_set is not exist')
            news_id_set,impression_id_to_clicked_news = behaviour_dataset.get_news_id_set_and_impression_id_to_clicked_news_dict()
            temp_dict = {
                "news_id_set":news_id_set,
                "impression_id_to_clicked_news":impression_id_to_clicked_news
            }
            torch.save(temp_dict,collection_all_news_id_and_all_impression_id_path)
        else:
            self.__logger.debug('all_news_id_set_and_impression_id_set  exist')
            temp_dict = torch.load(collection_all_news_id_and_all_impression_id_path)
            news_id_set = temp_dict["news_id_set"]
            impression_id_to_clicked_news = temp_dict["impression_id_to_clicked_news"]
        
        
        all_news_id_hash = self.__common_tool.calculate_md5_for_set_str(news_id_set)
        collection_news_id_to_embedding_file_name = f'collection_{config.embedding_model_name}_{config.embedding_model_version}_{all_news_id_hash}.pt'
        collection_news_id_to_embedding_dir = os.path.join(experiment_dir,"collection_news_id_to_embedding")
        if os.path.exists(collection_news_id_to_embedding_dir) is False:
            os.makedirs(collection_news_id_to_embedding_dir)
        collection_news_id_to_embedding_path = os.path.join(collection_news_id_to_embedding_dir,collection_news_id_to_embedding_file_name)
        content_similar_model = ContentSimilarModel(config)
        if os.path.exists(collection_news_id_to_embedding_path) is False or override_news_id_to_embedding:
            self.__logger.debug("news_id_to_embedding not exist")
            news_id_to_vector = dict()
            for current_news_id in tqdm(news_id_set,desc='calculate_news_id_to_embedding'):
                current_news_vector = content_similar_model.get_single_news_vector(current_news_id)
                news_id_to_vector[current_news_id] = current_news_vector
            torch.save(news_id_to_vector,collection_news_id_to_embedding_path)
        else:
            self.__logger.debug("news_id_to_embedding  exist")
            news_id_to_vector = torch.load(collection_news_id_to_embedding_path)
        
            
        
        '''
        all_impression_id_hash = self.__common_tool.calculate_md5_for_set_str(impression_id_to_clicked_news.keys())
        collection_impression_id_to_embedding_dir = os.path.join(experiment_dir,"collection_impression_id_to_embedding")
        collection_impression_id_to_embedding_file_name = f'collection_impression_{all_news_id_hash}.pt'
        collection_impression_id_to_embedding_path = os.path.join(collection_news_id_to_embedding_dir,collection_news_id_to_embedding_file_name)
        if os.path.exists(collection_impression_id_to_embedding_dir) is False:
            os.makedirs(collection_impression_id_to_embedding_dir)
        if os.path.exists(collection_all_news_id_and_all_impression_id_path) is False or override_impression_id_to_embedding:
            pass
        '''
            
        
        # put all news dataset into 
        behaviours_dataloader = iter(DataLoader(behaviour_dataset,
                                    batch_size=config.batch_size,
                                    shuffle=False,
                                    num_workers=config.num_workers,
                                    drop_last=False,
                                    pin_memory=True))
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        dnn_click_model = DNNClickPredictor(config,init_weight=True).to(device)
        best_model_path = os.path.join(experiment_dir,'best_model.pt')
        model_97_path = os.path.join(experiment_dir,'97_model.pt')
        model_199_path = os.path.join(experiment_dir,"199_model.pt")
        loss_model_path = os.path.join(experiment_dir,'loss_model.pt')
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(dnn_click_model.parameters(),
                                     lr=config.learning_rate)
        exhaustion_count = 0
        loss_full = []
        min_loss = sys.maxsize
        step = 0
        for i in tqdm(range(
            1,
            config.num_epochs * len(behaviour_dataset) // config.batch_size + 1),
                  desc="Training"):
            try:
                minibatch = next(behaviours_dataloader)
            except StopIteration:
                exhaustion_count += 1
                tqdm.write(
                    f"Training data exhausted for {exhaustion_count} times after {i} batches, reuse the dataset."
                )
                behaviours_dataloader = iter(
                    DataLoader(behaviour_dataset,
                            batch_size=config.batch_size,
                            shuffle=True,
                            num_workers=config.num_workers,
                            drop_last=True,
                            pin_memory=True))
                minibatch = next(behaviours_dataloader)
                # according click news calculate user vector
            candidate_news_str_list = minibatch["candidate_news_str"]
            # print(candidate_news_str_list)
            # print(clicked_news_list)
            clicked_news_str_list = minibatch["clicked_news_str"]
            # print(clicked_news_str_list)
            clicked_str_list = minibatch['clicked_str']
            list_user_embedding = list()
            list_candidate_news_embedding = list()
            list_label = list()
            
            for current_clicked_news_str,current_candidate_news_str,current_clicked_str  \
                in zip(clicked_news_str_list,candidate_news_str_list,clicked_str_list):
                    current_clicked_news_list = current_clicked_news_str.split()[:config.num_clicked_news_a_user]
                    if len(current_clicked_news_list) < 1:
                        self.__logger.debug(f'current_clicked_news_str {current_clicked_news_str} empty')
                        continue
                    current_user_embedding = content_similar_model.get_sinle_user_vector(current_clicked_news_list,news_id_to_vector)
                    # print(f'user_embedding_shape {current_user_embedding.shape}')
                    
                    current_candidate_news_list = current_candidate_news_str.split()
                    for current_candidate_news in current_candidate_news_list:
                        list_candidate_news_embedding.append(news_id_to_vector[current_candidate_news])
                    
                    current_clicked_list = current_clicked_str.split()
                    list_label.extend([int(current_clicked) for current_clicked in current_clicked_list])
                    
                    list_user_embedding.extend([current_user_embedding]*len(current_candidate_news_list))
            if len(list_user_embedding) < 1:
                self.__logger.debug(f'list_user_embedding empty')
                continue
            if len(list_candidate_news_embedding) < 1:
                self.__logger.debug('list_candidate_news_embedding empty')
                continue
            stack_user_embedding = torch.stack([current_user_embedding.to(device) for current_user_embedding in list_user_embedding],dim=0)
            stack_news_embedding = torch.stack([current_news_embedding.to(device) for current_news_embedding in list_candidate_news_embedding],dim=0)

            y_pred = dnn_click_model.forward(stack_news_embedding,stack_user_embedding)
            y = torch.FloatTensor(list_label).to(device)

            loss = criterion(y_pred, y)
            average_loss = loss.item()*1.0/ len(list_user_embedding)
        
            self.__logger.debug(f'current batch loss {average_loss}')
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if average_loss < min_loss:
                torch.save(
                    {
                    'model_state_dict':dnn_click_model.state_dict(),
                    'average_loss':average_loss
                    },best_model_path
                )
                min_loss = average_loss  
            
            if step % 97 == 0:
                torch.save(
                    {
                    'model_state_dict':dnn_click_model.state_dict(),
                    'average_loss':average_loss
                    },model_97_path
                )
            
            if step % 199 ==0:
                torch.save(
                    {
                    'model_state_dict':dnn_click_model.state_dict(),
                    'average_loss':average_loss
                    },model_199_path
                )
            
            
            if step % 100 == 0:
                loss_full.append(average_loss)
                torch.save({
                    "loss_full":loss_full
                },loss_model_path)        
            
            step = step + 1
                
            
            
            
            

            
                
                
                