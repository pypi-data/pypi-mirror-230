class Trust:
    """
    Trustworthiness score class containing its score and associated metrics and assessment method
    """

    def __init__(self):
        self.metrics = None
        self.assessment_method = None
        self.trust_dict = None
        self.trust_JSON = None
        self.trained_model = None
        self.data_x = None
        self.data_y = None
    
    def assess(self, trained_model, data_x, data_y):     
        """Performs the metrics' assessments, followed by the trust assessment
        based on such metrics and the specified assessment method and its parameters.

        Args:
            trained_model (classifier): classifier to evaluate
            data_x (pandas dataset): predictor data of the dataset to evaluate
            data_y (pandas dataset): target values of the dataset to evaluate
        """
        self.trained_model = trained_model
        self.data_x = data_x
        self.data_y = data_y

        for metric in self.metrics:
            metric.assess(self.trained_model, self.data_x, self.data_y)

        self.trust_dict, self.trust_JSON = self.assessment_method.assess()
    
    def get_metrics_assessment_dict(self) -> dict:
        """Returns a dictionary of shape Metric name (str) -> Metric assessment (float)

        Returns:
            dict: Metrics' assessments
        """
        metric_names = [metric.__class__.__name__ for metric in self.metrics]
        metric_assessments = [metric.score for metric in self.metrics]

        return dict(zip(metric_names, metric_assessments))