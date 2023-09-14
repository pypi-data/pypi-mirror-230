class Metric:
    """
    Metric abstract class
    """
      
    def __init__(self):
        self.score = None
    
    def assess(self, trained_model, data_x, data_y):
        """Assessment of the metric using the trained model, dataset predictors and targets passed as parameters.
        """

        pass