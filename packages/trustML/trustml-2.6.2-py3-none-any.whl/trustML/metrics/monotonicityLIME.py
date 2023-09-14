from trustML.metrics.metric import Metric
import pickle
import numpy as np
from aix360.metrics import monotonicity_metric

class MonotonicityLIMESKL(Metric):
    """Average Monotonicity metric of a sklearn-based classifier and a LIME explainer using the AIX360 package.

    This metric measures the effect of individual features on model performance by evaluating the effect on 
    model performance of incrementally adding each attribute in order of increasing importance. 
    As each feature is added, the performance of the model should correspondingly increase, 
    thereby resulting in monotonically increasing model performance.

    (Extracted from AIX360 documentation)

    ADDITIONAL PROPERTIES: 
    - explainer_path (str): filepath to a LIME explainer previously trained and stored as a pickle object

    Args:
        Metric (Class): Metric abstract class
    """
    
    def __init__(self, additional_properties):
        super().__init__()

        with open(additional_properties["explainer_path"], 'rb') as explainer_path:
            self.explainer = pickle.load(explainer_path)

    def assess(self, trained_model, data_x, data_y):
        print("Computing monotonicity metric with LIME...")
        ncases = data_x.values.shape[0]     
        monotonicity_vector = np.zeros(ncases) 
        for i in range(ncases):
            print("Case " + str(i+1) + "/" + str(ncases))
            explanation = self.explainer.explain_instance(
                data_x.values[i], trained_model.predict_proba, num_features=5, top_labels=1, num_samples=100)
            local_explanation = explanation.local_exp[next(iter(explanation.local_exp))]#explanation.local_exp[predicted_class]

            x = data_x.values[i]
            coefs = np.zeros(x.shape[0])
        
            for v in local_explanation:
                coefs[v[0]] = v[1]
            base = np.zeros(x.shape[0])

            monotonicity_vector[i] = monotonicity_metric(trained_model, data_x.values[i], coefs, base)

        self.score = np.mean(monotonicity_vector)