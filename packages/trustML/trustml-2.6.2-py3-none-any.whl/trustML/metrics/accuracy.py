from trustML.metrics.metric import Metric
from sklearn.metrics import accuracy_score

class AccuracySKL(Metric):
    """Accuracy classification score for sklearn-based classifiers using sklearn. In multilabel classification, 
    this function computes subset accuracy: the set of labels predicted for a sample must *exactly* match the 
    corresponding set of ground truth labels.
    
    (Extracted from sklearn documentation).

    ADDITIONAL PROPERTIES:
    None
    
    Args:
        Metric (Class): Metric abstract class
    """

    def __init__(self):
        super().__init__()
        
    def assess(self, trained_model, data_x, data_y):
        pred = trained_model.predict(data_x)
        self.score = accuracy_score(data_y, pred)