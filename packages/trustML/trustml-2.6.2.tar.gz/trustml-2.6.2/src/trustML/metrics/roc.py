from trustML.metrics.metric import Metric
from sklearn.metrics import roc_auc_score

class ROCSKL(Metric):
    """ROC score for sklearn-based classifiers using sklearn. It computes the Area Under the 
    Receiver Operating Characteristic Curve (ROC AUC) from prediction scores.

    (Extracted from sklearn documentation)

    ADDITIONAL PROPERTIES:
    multiclass_average (str): 'macro' for binary classification problems, for 
    multiclass/multilabel targets, 'macro' or 'weighted'.

    Args:
        Metric (Class): Metric abstract class
    """
      
    def __init__(self, additional_properties):
        super().__init__()
        self.multiclass_average = additional_properties["multiclass_average"]

    def assess(self, trained_model, data_x, data_y):
        pred = trained_model.predict(data_x)
        self.score = roc_auc_score(data_y, pred, average=self.multiclass_average)