from trustML.metrics.metric import Metric
import pickle

class ExplanationsAccuracyTED(Metric):
    """Accuracy of a TED-enhanced classifier using a test dataset. TED is an explainability 
    framework that leverages domain-relevant explanations in the training dataset to predict 
    both labels and explanations for new instances. (Extracted from TED_Cartesian documentation).

    ADDITIONAL PROPERTIES: 
    - explainer_path (str): filepath to a TED-enhanced classified previously stored as a pickle object
    - explanations_path (str): filepath to a pandas dataset of explanations corresponding to the dataset's 
    instances (i.e., rows) composed of features (dataX) and targets (dataY)

    Args:
        Metric (Class): Metric abstract class
    """
    
    def __init__(self, additional_properties):
        super().__init__()

        with open(additional_properties["explainer_path"], 'rb') as explainer_path:
            self.explainer = pickle.load(explainer_path)

        with open(additional_properties["explanations_path"], 'rb') as explanations_path:
            self.data_E = pickle.load(explanations_path)

    def assess(self, trained_model, data_x, data_y):
        YE_accuracy, Y_accuracy, E_accuracy = self.explainer.score(
            data_x, data_y, self.data_E)
        self.score = YE_accuracy