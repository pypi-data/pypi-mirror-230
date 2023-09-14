from trustML.metrics.metric import Metric
import numpy as np
import pickle
from sklearn.preprocessing import MinMaxScaler
from aix360.metrics import faithfulness_metric

class FaithfulnessLIMESKL(Metric):
    """Average Faithfulness metric of a sklearn-based classifier and a LIME explainer using the AIX360 package.

    This metric evaluates the correlation between the importance assigned by the interpretability algorithm 
    to attributes and the effect of each of the attributes on the performance of the predictive model. 
    The higher the importance, the higher should be the effect, and vice versa, The metric evaluates
    this by incrementally removing each of the attributes deemed important by the interpretability metric,
    and evaluating the effect on the performance, and then calculating the correlation between the weights
    (importance) of the attributes and corresponding model performance.

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
        print("Computing faithfulness metric with LIME...")
        ncases = data_x.values.shape[0]     
        faithfulness_vector = np.zeros(ncases) 
        for i in range(ncases):
            print("Case " + str(i+1) + "/" + str(ncases), end="\r")
            explanation = self.explainer.explain_instance(
                data_x.values[i], trained_model.predict_proba, num_features=5, top_labels=1, num_samples=100)
            local_explanation = explanation.local_exp[next(iter(explanation.local_exp))]#explanation.local_exp[predicted_class]

            x = data_x.values[i]
            coefs = np.zeros(x.shape[0])
        
            for v in local_explanation:
                coefs[v[0]] = v[1]
            base = np.zeros(x.shape[0])

            faithfulness_vector[i] = faithfulness_metric(trained_model, data_x.values[i], coefs, base)
        scaler = MinMaxScaler()
        faithfulness_vector_scaled = scaler.fit_transform(faithfulness_vector.reshape(-1,1)) 
        # COMPUTED FROM -1 TO 1, WE SCALED IT TO 0-1 WITH MINMAX

        self.score = np.mean(faithfulness_vector_scaled)
    
