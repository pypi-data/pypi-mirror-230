import numpy as np
from trustML.metrics.metric import Metric
from sklego.metrics import equal_opportunity_score

class EqualOpportunitySKL(Metric):
    """Equal opportunity metric of a sklearn-based classifier using sklego. The equality opportunity 
    score calculates the ratio between the probability of a **true positive** outcome given the sensitive 
    attribute (column) being true and the same probability given the sensitive attribute being false.

    This is especially useful to use in situations where "fairness" is a theme.

    (Extracted from sklego documentation)

    ADDITIONAL PROPERTIES: 
    - protected_attributes (list of str): list of sensible features
    - positive_class (optional): privileged class (if present, 1 otherwise)

    Args:
        Metric (Class): Metric abstract class
    """
    
    def __init__(self, additional_properties):
        super().__init__()
        self.protected_attributes = additional_properties["protected_attributes"]
        if "positive_class" in additional_properties:
            self.positive_class = additional_properties["positive_class"]
        else:
            self.positive_class = 1

    def assess(self, trained_model, data_x, data_y):    
        print("Computing equal opportunity metric...")
        if (self.protected_attributes is None):
            self.score = 1
        else:
            eq_opp_vector = np.zeros(len(self.protected_attributes))
            for i in range(len(self.protected_attributes)):
                eq_opp_vector[i] = equal_opportunity_score(
                    sensitive_column = self.protected_attributes[i], 
                    positive_target=self.positive_class)(trained_model, data_x, data_y)
                                  
            self.score = np.mean(eq_opp_vector)
