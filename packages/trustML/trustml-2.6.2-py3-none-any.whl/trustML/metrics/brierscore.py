from trustML.metrics.metric import Metric
from uq360.metrics.classification_metrics import multiclass_brier_score

class InvertedBrierSKL(Metric):
    """Inverted brier score metric of a sklearn-based classifier using UQ360.

    This metric is used to measure to compare true observed labels with predicted
    probabilities in multiclass classification tasks. Although it is a cost function, 
    its assessment is inverted so it can be treated as the rest of metrics (i.e., as a percentage).

    ADDITIONAL PROPERTIES:
    None
    
    Args:
        Metric (Class): Metric abstract class
    """

    def __init__(self):
        super().__init__()

    def assess(self, trained_model, data_x, data_y):
        print("Computing inverted brier uncertainty metric...")
        prediction_proba = trained_model.predict_proba(data_x)
        
        brier_score = multiclass_brier_score(data_y, prediction_proba)        

        self.score = (1-brier_score)