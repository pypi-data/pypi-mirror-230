from ast import literal_eval
import os
import pandas as pd
import torch
from torch.utils.data import Dataset


from recommend_model_sdk.mind_sdk.config.mind_base_config import MINDBaseConfig

class MINDNewsDataset(Dataset):
    """
    Load news for evaluation.
    """
    def __init__(self, news_path,config):
        """_summary_

        Args:
            news_path (_type_): _description_ new_path is news_parsed.tsv, not news.tsv
            config (_type_): _description_

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """
        super(MINDNewsDataset, self).__init__()
        if isinstance(config,MINDBaseConfig) is False:
            raise ValueError("config is not MINDBaseConfig")
        if isinstance(news_path,str) is False:
            raise ValueError("news_path is not str")
        if os.path.exists(news_path) is False:
            raise ValueError("news_path is not exist")
        
        self.config = config
        self.news_parsed = pd.read_table(
            news_path,
            usecols=['id'] + self.config.dataset_attributes['news'],
            converters={
                attribute: literal_eval
                for attribute in set(self.config.dataset_attributes['news']) & set([
                    'title', 'abstract', 'title_entities', 'abstract_entities'
                ])
            } # converters can be removed
            )
        # to do check news_parsed
        self.news2dict = self.news_parsed.to_dict('index')
        for key1 in self.news2dict.keys():
            for key2 in self.news2dict[key1].keys():
                if type(self.news2dict[key1][key2]) != str:
                    self.news2dict[key1][key2] = torch.tensor(
                        self.news2dict[key1][key2])

    def __len__(self):
        return len(self.news_parsed)

    def __getitem__(self, idx):
        item = self.news2dict[idx]
        return item
    
    def get_news_id_set(self):
        news_id_set = set()
        for current_idex,current_item in self.news2dict.items():
            news_id_set.add(current_item["id"])
        return news_id_set