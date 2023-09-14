from trustML.metrics.metric import Metric
from art.metrics import RobustnessVerificationTreeModelsCliqueMethod
from art.estimators.classification import SklearnClassifier
import pandas as pd

class VerifiedErrorSKLTree(Metric):
    """Verified error of a decision-tree sklearn-based model on the provided dataset (dataX, dataY) 
    using the ART package.

    This metric is typically used to verify the robustness of the classifier on the provided dataset. 
    Although it is a cost function, its assessment is inverted so it can be treated as the rest of metrics 
    (i.e., as a percentage).
   
    ADDITIONAL PROPERTIES:
    None

    Args:
        Metric (Class): Metric abstract class
    """
    
    def __init__(self):
        super().__init__()

    def assess(self, trained_model, data_x, data_y):
        print("Computing verified error...")
        rf_skmodel = SklearnClassifier(model=trained_model)
        rt = RobustnessVerificationTreeModelsCliqueMethod(classifier=rf_skmodel)        
        average_bound, verified_error = rt.verify(x=data_x.values, y=pd.get_dummies(data_y).values, eps_init=0.001,
         nb_search_steps=1, max_clique=2, max_level=1)

        self.score = (1-verified_error) # INVERT THE ERROR TO GET THE SCORE