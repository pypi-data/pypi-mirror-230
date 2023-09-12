import pandas as pd
from torch.utils.data import Dataset, DataLoader

from recommend_model_sdk.mind_sdk.config.mind_base_config import MINDBaseConfig

class MINDBehaviorsDataset(Dataset):
    """
    Load behaviors for evaluation, (user, time) pair as session
    """
    def __init__(self, behaviors_path,config):
        """_summary_

        Args:
            behaviors_path (_type_): _description_ is behaviors.tsv. not behaviors_parsed.tsv
            config (_type_): _description_

        Raises:
            ValueError: _description_
        """
        super(MINDBehaviorsDataset, self).__init__()
        if isinstance(config,MINDBaseConfig) is False:
            raise ValueError("config is not MINDBaseConfig")
        self.__config = config
        self.behaviors = pd.read_table(behaviors_path,
                                       header=None,
                                       usecols=range(5),
                                       names=[
                                           'impression_id', 'user', 'time',
                                           'clicked_news', 'impressions'
                                       ])
        self.behaviors.clicked_news.fillna(' ', inplace=True)
        self.behaviors.impressions = self.behaviors.impressions.str.split()

    def __len__(self):
        return len(self.behaviors)

    def __getitem__(self, idx):
        row = self.behaviors.iloc[idx]
        item = {
            "impression_id": row.impression_id,
            "user": row.user,
            "time": row.time,
            "clicked_news_string": row.clicked_news,
            "impressions": row.impressions,
            "clicked_news":row.clicked_news.split()[:self.__config.num_clicked_news_a_user]
        }
        return item