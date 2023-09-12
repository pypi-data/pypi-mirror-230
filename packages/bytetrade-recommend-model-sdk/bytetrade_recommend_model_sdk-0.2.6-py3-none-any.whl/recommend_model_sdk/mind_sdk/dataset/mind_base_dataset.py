from ast import literal_eval
import os
import pandas as pd
import torch
from torch.utils.data import Dataset

from recommend_model_sdk.mind_sdk.config.mind_base_config import MINDBaseConfig


class MINDBaseDataset(Dataset):
    
    def __init__(self,config,behaviors_path,news_path) -> None:
        """_summary_
        used for train
        Args:
            config (_type_): _description_
            behaviors_path (_type_): _description_ is behaviors_parsed.tsv, not behaviors.tsv
            news_path (_type_): _description_ is news_parsed.tsv, not news.tsv

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """
        super(MINDBaseDataset).__init__()
        if isinstance(config,MINDBaseConfig) is False:
            raise ValueError("config is not ")
        if isinstance(behaviors_path,str) is False:
            raise ValueError("behaviors_path is not str")
        if os.path.exists(behaviors_path) is False:
            raise ValueError(f"behaviors_path {behaviors_path} is not exist")
        if isinstance(news_path,str) is False:
            raise ValueError("news_path is not str")
        if os.path.exists(news_path) is False:
            raise ValueError(f"news_path {news_path} is not exist")
        
        self.__config = config
        self.behaviors_parsed = pd.read_table(behaviors_path)
        self.news_parsed = pd.read_table(
            news_path,
            index_col='id',
            usecols=['id'] + config.dataset_attributes['news'],
            
            # converters={
            #    attribute: literal_eval
            #    for attribute in set(config.dataset_attributes['news']) & set([
            #        'title', 'abstract', 'title_entities', 'abstract_entities'
            #    ])
            #}
            
            converters={
                attribute: literal_eval
                for attribute in set([
                    'title', 'abstract', 'title_entities', 'abstract_entities'
                ])
            }
            )
        self.news_id2int = {x: i for i, x in enumerate(self.news_parsed.index)}
        self.news2dict = self.news_parsed.to_dict('index')
        for key1 in self.news2dict.keys():
            for key2 in self.news2dict[key1].keys():
                self.news2dict[key1][key2] = torch.Tensor(
                    self.news2dict[key1][key2])
        # padding_all     
        
        padding_all = {
            'category': 0,
            'subcategory': 0,
            'title': [0] * config.num_words_title,
            'abstract': [0] * config.num_words_abstract,
            'title_entities': [0] * config.num_words_title,
            'abstract_entities': [0] * config.num_words_abstract
        }
        for key in padding_all.keys():
            padding_all[key] = torch.Tensor(padding_all[key])

        self.padding = {
            k: v
            for k, v in padding_all.items()
            if k in config.dataset_attributes['news']
        }
        
        self.__parsed_behaviour_attribute = ['user,clicked_news','candidate_news','clicked']

    def __len__(self):
        return len(self.behaviors_parsed)

    def __getitem__(self, idx):
        item = {}
        row = self.behaviors_parsed.iloc[idx]
        if 'user' in self.__parsed_behaviour_attribute:
            item['user'] = row.user
        item["clicked"] = list(map(int, row.clicked.split()))
        item["candidate_news"] = [
            self.news2dict[x] for x in row.candidate_news.split()
        ]
        item["clicked_news"] = [
            self.news2dict[x]
            for x in row.clicked_news.split()[:self.__config.num_clicked_news_a_user]
        ]
        if 'clicked_news_length' in self.__parsed_behaviour_attribute:
            item['clicked_news_length'] = len(item["clicked_news"])
        repeated_times = self.__config.num_clicked_news_a_user - \
            len(item["clicked_news"])
        assert repeated_times >= 0
        
        item["clicked_news"] = [self.padding
                                ] * repeated_times + item["clicked_news"]
        

        return item
