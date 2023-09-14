from trustML.metrics.metric import Metric
from sklearn.metrics import recall_score

class RecallSKL(Metric):
    """Recall score for sklearn-based classifiers using sklearn. The recall is the ratio tp / (tp + fn) 
    where tp is the number of true positives and fn the number of false negatives. 
    The recall is intuitively the ability of the classifier to find all the positive samples.

    The best value is 1 and the worst value is 0.

    (Extracted from sklearn documentation)

    ADDITIONAL PROPERTIES:
    multiclass_average (str): 'binary' for binary classification problems, for 
    multiclass/multilabel targets, 'micro', 'macro', 'samples' or 'weighted'.

    Args:
        Metric (Class): Metric abstract class
    """
    
    def __init__(self, additional_properties):
        super().__init__()
        self.multiclass_average = additional_properties["multiclass_average"]

    def assess(self, trained_model, data_x, data_y):
        pred = trained_model.predict(data_x)
        self.score = recall_score(data_y, pred, average=self.multiclass_average)