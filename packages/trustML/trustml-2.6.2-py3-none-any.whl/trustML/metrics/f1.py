from trustML.metrics.metric import Metric
from sklearn.metrics import f1_score

class F1SKL(Metric):
    """F1 score for sklearn-based classifiers, using sklearn. The F1 score can be interpreted 
    as a weighted average of the precision and recall, where an F1 score reaches its best
    value at 1 and worst score at 0. The relative contribution of precision and recall 
    to the F1 score are equal. The formula for the F1 score is:

    F1 = 2 * (precision * recall) / (precision + recall)

    (Extracted from sklearn documentation)

    ADDITIONAL PROPERTIES:
    multiclass_average (str): 'binary' for binary classification problems, for 
    multiclass/multilabel targets, 'micro', 'macro' or 'weighted'.

    Args:
        Metric (Class): Metric abstract class
    """
    
    def __init__(self, additional_properties):
        super().__init__()
        self.multiclass_average = additional_properties["multiclass_average"]
        

    def assess(self, trained_model, data_x, data_y):
        pred = trained_model.predict(data_x)
        self.score = f1_score(data_y, pred, average=self.multiclass_average)
