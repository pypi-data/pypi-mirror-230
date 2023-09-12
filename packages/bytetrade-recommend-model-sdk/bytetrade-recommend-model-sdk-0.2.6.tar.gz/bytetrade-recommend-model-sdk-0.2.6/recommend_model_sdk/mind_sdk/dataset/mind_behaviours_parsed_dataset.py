import pandas as pd
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
from recommend_model_sdk.mind_sdk.config.mind_base_config import MINDBaseConfig

class MINDBehaviorsParsedDataset(Dataset):
    """
    Load behaviors for evaluation, (user, time) pair as session
    """
    def __init__(self, behaviors_path,config):
        """_summary_

        Args:
            behaviors_path (_type_): _description_ is behaviors_parsed.tsv. not behaviors.tsv
            config (_type_): _description_

        Raises:
            ValueError: _description_
        """
        super(MINDBehaviorsParsedDataset, self).__init__()
        if isinstance(config,MINDBaseConfig) is False:
            raise ValueError("config is not MINDBaseConfig")
        self.__config = config
        self.__behaviors = pd.read_table(behaviors_path,
                                       header=None,
                                       skiprows=[0],
                                       # usecols=range(4),
                                       names=[
                                           'user', 'clicked_news',
                                           'candidate_news', 'clicked','impression_id'
                                       ])
        # self.__behaviors.clicked_news.fillna(' ', inplace=True)

    def __len__(self):
        return len(self.__behaviors)

    def __getitem__(self, idx):
        row = self.__behaviors.iloc[idx]
        item = {
            "user": row.user,
            # "candidate_news": row.candidate_news.split(),
            "candidate_news_str": row.candidate_news,
            'clicked_str': row.clicked,
            # 'clicked':row.clicked.split(),
            "impression_id": row.impression_id,
            "impression_id_str":str(row.impression_id),
            # "clicked_news":row.clicked_news.split()[:self.__config.num_clicked_news_a_user],
            'clicked_news_str':row.clicked_news
        }
        return item
    
    
    def get_news_id_set_and_impression_id_to_clicked_news_dict(self):
        news_id_set = set()
        impression_id_to_clicked_news_dict = dict()
        for current_index in tqdm(range(len(self.__behaviors)),desc="get_all_news_id_and_impression_id"):
            current_row = self.__getitem__(current_index)
            for current_news_id in current_row['clicked_news']:
                news_id_set.add(current_news_id)
            for current_news_id in current_row['candidate_news']:
                news_id_set.add(current_news_id)
            impression_id_to_clicked_news_dict[current_row["impression_id"]] = current_row["clicked_news"]
            
        return news_id_set,impression_id_to_clicked_news_dict
    
    