from trustML.metrics.metric import Metric
from art.metrics import RobustnessVerificationTreeModelsCliqueMethod
from art.estimators.classification import SklearnClassifier
import pandas as pd

class AverageBoundSKLTree(Metric):
    """Average robustness bound of a decision-tree sklearn-based model on the provided dataset 
    (data_x, data_y) using the ART package.

    This metric is typically used to verify the robustness of the classifier on the provided dataset.
   
    Args:
        Metric (Class): Metric abstract class
    """
    
    def __init__(self):
        super().__init__()

    def assess(self, trained_model, data_x, data_y):
        print("Computing average robustness bound metric...")
        rf_skmodel = SklearnClassifier(model=trained_model)
        rt = RobustnessVerificationTreeModelsCliqueMethod(classifier=rf_skmodel)        
        average_bound, verified_error = rt.verify(x=data_x.values, y=pd.get_dummies(data_y).values, eps_init=0.001, 
        nb_search_steps=1, max_clique=2, max_level=1)

        self.score = average_bound