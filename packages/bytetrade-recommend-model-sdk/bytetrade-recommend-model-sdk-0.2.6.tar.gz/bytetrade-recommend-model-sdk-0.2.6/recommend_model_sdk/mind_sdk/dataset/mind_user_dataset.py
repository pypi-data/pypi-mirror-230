import os
import pandas as pd
from torch.utils.data import Dataset, DataLoader


from recommend_model_sdk.mind_sdk.config.mind_base_config import MINDBaseConfig

class MINDUserDataset(Dataset):
    def __init__(self, behaviors_path, user2int_path,config):
        """_summary_

        Args:
            behaviors_path (_type_): _description_ here behaviors is not behaviors_parsed.tsv, but is behaviors.tsv
            user2int_path (_type_): _description_ user2int.tsv
            config (_type_): _description_

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """
        super(MINDUserDataset, self).__init__()
        if isinstance(config,MINDBaseConfig) is False:
            raise ValueError("config is not ")
        if isinstance(behaviors_path,str) is False:
            raise ValueError("behaviors_path is not str")
        if os.path.exists(behaviors_path) is False:
            raise ValueError("behaviors_path is not exist")
        if isinstance(user2int_path, str) is False:
            raise ValueError("user2int_path is not str")
        if os.path.exists(user2int_path) is False:
            raise ValueError(f'{user2int_path} is not exist')
        self.config = config
        self.behaviors = pd.read_table(behaviors_path,
                                       header=None,
                                       usecols=[1, 3],
                                       names=['user', 'clicked_news'])
        self.behaviors.clicked_news.fillna(' ', inplace=True)
        self.behaviors.drop_duplicates(inplace=True)
        user2int = dict(pd.read_table(user2int_path).values.tolist())
        user_total = 0
        user_missed = 0
        
        # not necessary convert user 
        for row in self.behaviors.itertuples():
            user_total += 1
            if row.user in user2int:
                self.behaviors.at[row.Index, 'user'] = user2int[row.user]
            else:
                user_missed += 1
                self.behaviors.at[row.Index, 'user'] = 0


    def __len__(self):
        return len(self.behaviors)

    def __getitem__(self, idx):
        row = self.behaviors.iloc[idx]
        item = {
            "user":
            row.user,
            "clicked_news_string":
            row.clicked_news,
            "clicked_news":
            row.clicked_news.split()[:self.config.num_clicked_news_a_user]
        }
        item['clicked_news_length'] = len(item["clicked_news"])
        repeated_times = self.config.num_clicked_news_a_user - len(
            item["clicked_news"])
        assert repeated_times >= 0
        item["clicked_news"] = ['PADDED_NEWS'
                                ] * repeated_times + item["clicked_news"]

        return item