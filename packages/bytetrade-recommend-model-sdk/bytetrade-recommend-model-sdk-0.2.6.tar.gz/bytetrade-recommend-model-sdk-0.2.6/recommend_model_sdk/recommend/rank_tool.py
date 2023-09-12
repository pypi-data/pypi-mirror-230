import copy
from imblearn.over_sampling import RandomOverSampler
import numpy as np
import os
import random
from sklearn.model_selection import train_test_split
import time
import xgboost as xgb
from xgboost import XGBClassifier

from recommend_model_sdk.tools.common_tool import CommonTool
from recommend_model_sdk.tools.model_tool import ModelTool


class CTRRankTool:
    """_summary_
    Click Through Rate
    """
    def __init__(self,model_root_dir) -> None:
        self.__ros = RandomOverSampler(random_state=0)
        self.__common_tool = CommonTool()
        self.__logger = self.__common_tool.get_logger()
        if isinstance(model_root_dir,str) is False:
            raise ValueError("model_root_dir is not str")
        if os.path.exists(model_root_dir) is False:
            raise ValueError("model_root_dir is not exist")
        self.__model_root_dir = model_root_dir
        self.__recommend_model_root_dir = os.path.join(model_root_dir,"recommend")
        if os.path.exists(self.__recommend_model_root_dir) is False:
            os.makedirs(self.__recommend_model_root_dir)
        # self.__recommend_model_path = os.path.join(self.__recommend_model_root_dir,"ctr.json")
        # self.__performance_path = os.path.join(self.__recommend_model_root_dir,"performance.json")
        self.__model_tool = ModelTool(model_root_dir)


    
    def batch_next(self,iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]
            
    def validate_entry_id_set(self,entry_id_set):
        if isinstance(entry_id_set,set) is False:
            raise ValueError("entry_id_set is not set")
        for current_entry_id in  entry_id_set:
            if isinstance(current_entry_id,int) is False:
                raise ValueError("current_entry_id is not int")
    
    def configure_positive_and_negative_sample_ratio(self, positive_entry_id_set,negative_entry_id_set,embedding_dim):
        """_summary_
        
        Args:
            positive_entry_id_set (_type_): _description_
            negative_entry_id_set (_type_): _description_
            embedding_dim (_type_): _description_
        """
        if isinstance(embedding_dim,int) is False:
            raise ValueError("embedding_dim is not int")
        if embedding_dim < 1:
            raise ValueError("embedding_dim is small than 1")
        majority_number = max(len(positive_entry_id_set),len(negative_entry_id_set))
        
        if 2 * ( majority_number * 0.9 ) < 20:
            self.__logger.debug(f'2 * ( majority_number * 0.9 ) < 20  {2 * ( majority_number * 0.9 ) } < 20')
            return [],[]
        if len(positive_entry_id_set) < 10:
            self.__logger.debug(f'positive_entry_id_set length small than 10')
            return [],[]
        self.__logger.debug(f'positive_entry_id_set {len(positive_entry_id_set)} negative_entry_id_set {len(negative_entry_id_set)}')
        positive_train_x,positive_test_x,positive_train_y,positive_test_y = train_test_split(list(positive_entry_id_set),[1]*len(positive_entry_id_set),test_size=0.1)
        negative_train_x, negative_test_x,negative_train_y,negative_test_y = train_test_split(list(negative_entry_id_set),[0]*len(negative_entry_id_set),test_size=0.1)
        
        self.__logger.debug(f'positive_train_x {type(positive_train_x)} {len(positive_train_x)} negative_train_x {len(negative_train_x)}')
        positive_train_x.extend(negative_train_x)
        positive_train_y.extend(negative_train_y)
        
        positive_test_x.extend(negative_test_x)
        positive_test_y.extend(negative_test_y)
        # process 

        train_x_array = np.asarray(positive_train_x)
        train_x_array = train_x_array.reshape((-1,1))

        train_y_array = np.asarray(positive_train_y)
        resampled_x, resampled_y = self.__ros.fit_resample(train_x_array, train_y_array)
        train_tuple = list()

        for current_x,current_y in list(zip(resampled_x,resampled_y)):
            train_tuple.append((int(current_x[0]),int(current_y)))
            # train_tuple.append(current_x[])
        test_tuple = list(zip(positive_test_x,positive_test_y))
        return train_tuple,test_tuple
        
            
    def whether_break(self,start_time,duration_max):
        if isinstance(start_time,int) is False and isinstance(start_time,float) is False:
            raise ValueError("start_time is not int")
        if start_time < 1:
            raise ValueError("start_time should bigger than 1")
        if isinstance(duration_max,int) is False:
            raise ValueError("duration_max is not int")
        if duration_max < 1:
            raise ValueError("duration_max is not int")
        
        if time.time() - start_time > duration_max:
            return True
        else:
            return False
        
    def predict(self,current_embedding,model_name,model_version):
        """_summary_

        Args:
            current_embedding (_type_): _description_
            model_name (_type_): _description_
            model_version (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
            two lists:[0, 0, 1, 1, 0, 0, 1, 1, 1, 0]   
            [1.7693946574581787e-05, 0.19826048612594604, 0.991330623626709, 0.9989664554595947, 0.13013482093811035, 3.902898606611416e-05, 0.997657060623169, 0.999998927116394, 0.9999996423721313, 2.1516236301977187e-05]
        """
        if self.whether_can_predict(current_embedding,model_name,model_version) is False:
            raise ValueError("can not predict")
        recommend_model_path = os.path.join(self.__recommend_model_root_dir,f"{model_name}_{model_version}_ctr.json")
        performance_path = os.path.join(self.__recommend_model_root_dir,f"{model_name}_{model_version}_performance.json")
        sklearn_model = xgb.XGBClassifier()
        sklearn_model.load_model(recommend_model_path)
        predict_label = sklearn_model.predict(current_embedding)
        predict_proba = sklearn_model.predict_proba(current_embedding)
        return predict_label.tolist(),predict_proba[:,1].tolist()
    
    def whether_can_predict(self,current_embedding,model_name,model_version):
        if isinstance(current_embedding,np.ndarray) is False:
            raise ValueError("current_embedding is not np.ndarray")
        if current_embedding.ndim != 2:
            raise ValueError("current_embedding ndim is not equal 2")
        current_model_detail = self.__model_tool.valid_model_name_and_version(model_name,model_version)
        embedding_dimension = current_model_detail["embedding_dim"]
        recommend_model_path = os.path.join(self.__recommend_model_root_dir,f"{model_name}_{model_version}_ctr.json")
        performance_path = os.path.join(self.__recommend_model_root_dir,f"{model_name}_{model_version}_performance.json")
        if (os.path.exists(recommend_model_path) is False or 
            os.path.exists(performance_path) is False):
            self.__logger.debug(f'rank model not exist')
            return False
        performance = self.__common_tool.read_json(performance_path)
        if current_embedding.shape[1] != embedding_dimension:
            self.__logger.debug('data dimension not equal model dimension')
            return False
        return True
        

    
    def train(self,positive_entry_id_set,negative_entry_id_set,model_name,model_version,method_according_entry_id_and_label_to_get_embedding,duration_max=1200):
        """_summary_
        def method_according_entry_id_and_label_to_get_embedding(entry_id_and_label_tuple_list):
            return train_x_embedding, train_y_embedding
        Args:
            positive_entry_id_set (_type_): _description_
            negative_entry_id_set (_type_): _description_
            embedding_dimension (_type_): _description_
            method_according_entry_id_set_to_get_embedding (_type_): _description_

        Raises:
            ValueError: _description_
        """
        self.validate_entry_id_set(positive_entry_id_set)
        self.validate_entry_id_set(negative_entry_id_set)
        current_model_detail = self.__model_tool.valid_model_name_and_version(model_name,model_version)
        embedding_dimension = current_model_detail["embedding_dim"]

        entry_id_to_click_label = dict()
        for current_positive_entry_id in positive_entry_id_set:
            entry_id_to_click_label[current_positive_entry_id] = 1
        for current_negative_entry_id in negative_entry_id_set:
            entry_id_to_click_label[current_negative_entry_id] = 0
        iterations = 1
        
        train_tuple_list,test_tuple_list = self.configure_positive_and_negative_sample_ratio(positive_entry_id_set,negative_entry_id_set,embedding_dimension)
        if len(train_tuple_list) == 0:
            self.__logger.debug("can not configure proper train_tuple_list")
            return
        random.shuffle(train_tuple_list)
        random.shuffle(test_tuple_list)
        # 
        current_eval_metric = ["auc"]
        parameter_dict = {'max_depth': [4,5,6,7],
                    'n_estimators': [5,10,20],
                    'learning_rate': [0.3,0.5,0.7]}
        common_tool = CommonTool()
        list_parameter_dict = common_tool.make_combination_parameter(parameter_dict)
        self.__logger.debug(f'train_tuple_list {len(train_tuple_list)}')
        epoch_number = 10
        best_model = None
        best_average_auc = -10000
        start_time = time.time()
        earlier_stop = False
        for current_parameter_dict in list_parameter_dict:
            self.__logger.debug(f'current_parameter_dict {current_parameter_dict}')
            sklearn_model = xgb.XGBClassifier(max_depth=current_parameter_dict["max_depth"],learning_rate= current_parameter_dict["learning_rate"], n_estimators=current_parameter_dict["n_estimators"],
                                               verbosity=0, objective='binary:logistic',random_state=1,num_class = 1)

            iterations = 1
            for current_epoch in range(1,epoch_number):
                for current_batch_entry_id_and_label_tuple_list in self.batch_next(train_tuple_list,1000):
                    current_train_x_batch_embeddding,current_train_y_batch_label = method_according_entry_id_and_label_to_get_embedding(current_batch_entry_id_and_label_tuple_list)
                    if isinstance(current_train_x_batch_embeddding,np.ndarray) is False:
                        raise ValueError("x_batch_embedding is not numpy ndarray")
                    if isinstance(current_train_y_batch_label,np.ndarray) is False:
                        raise ValueError("y_batch_label is not numpy ndarray")
                    if current_train_x_batch_embeddding.shape[0] != current_train_y_batch_label.shape[0]:
                        raise ValueError("entrx_batch_embeddding number of items not equal y_batch_label")
                    if len(test_tuple_list) > 100:
                        temp_test_tuple_list = random.sample(test_tuple_list,100)
                    else:
                        temp_test_tuple_list = test_tuple_list
                    current_test_x_batch_embedding,current_test_y_batch_label = method_according_entry_id_and_label_to_get_embedding(temp_test_tuple_list)
                    current_eval_set = [(current_test_x_batch_embedding, current_test_y_batch_label)]
                    self.__logger.debug(f'{current_train_x_batch_embeddding.shape}  {current_train_y_batch_label.shape}')
                    if (iterations == 1):
                        sklearn_model = sklearn_model.fit(current_train_x_batch_embeddding, current_train_y_batch_label, eval_set=current_eval_set,
                                verbose=False, eval_metric = current_eval_metric,
                                early_stopping_rounds = 1, 
                                )
                    else:

                        sklearn_model = sklearn_model.fit(current_train_x_batch_embeddding, current_train_y_batch_label, eval_set=current_eval_set,
                                verbose=False, eval_metric = current_eval_metric,
                                early_stopping_rounds = 1, 
                                xgb_model = sklearn_model

                                )
                    iterations = iterations + 1
                current_eval_result = sklearn_model.evals_result()
                current_auc_list = current_eval_result["validation_0"]["auc"]
                sum_auc = 0
                for current_auc in current_auc_list:
                    sum_auc = sum_auc + current_auc
                current_average_auc = sum_auc / len(current_auc_list)
                self.__logger.debug(f'current_average_auc {current_average_auc} epoch')
                    
                self.__logger.debug(f'current_eval_result {current_eval_result}')
                if best_model is None or current_average_auc > best_average_auc:
                    best_model = copy.deepcopy(sklearn_model)
                    best_average_auc = current_average_auc
                if self.whether_break(start_time,duration_max):
                    earlier_stop = True
                    break
            if earlier_stop:
                break
            
                # best_model.save_model(f'current_bestk_epoch_{current_epoch}_{best_epoch}.json')
        self.__logger.debug(f'train time duration {time.time()-start_time} earlier_stop {earlier_stop}')        
            
        recommend_model_path = os.path.join(self.__recommend_model_root_dir,f"{model_name}_{model_version}_ctr.json")
        performance_path = os.path.join(self.__recommend_model_root_dir,f"{model_name}_{model_version}_performance.json")
        best_model.save_model(recommend_model_path)
        
        performance_dict = {
            "auc":best_average_auc,
            "model_name":model_name,
            "model_version":model_version
        }
        self.__common_tool.write_json(performance_dict,performance_path)
        
        # get evaluation
        
        # upload model to s3