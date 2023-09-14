from trustML.metrics.metric import Metric
from uq360.metrics.classification_metrics import expected_calibration_error

class InvertedExpectedCalibrationSKL(Metric):
    """Inverted brier score metric of a sklearn-based classifier using UQ360.

    This metric measures the difference in expectation between confidence and accuracy. 
    Although it is a cost function, its assessment is inverted so it can be treated as 
    the rest of metrics (i.e., as a percentage).

    Chuan Guo, Geoff Pleiss, Yu Sun, Kilian Q. Weinberger; Proceedings of the 34th 
    International Conference on Machine Learning, PMLR 70:1321-1330, 2017.

    ADDITIONAL PROPERTIES:
    None

    Args:
        Metric (Class): Metric abstract class
    """

    def __init__(self):
        super().__init__()

    def assess(self, trained_model, data_x, data_y):
        print("Computing expected calibration uncertainty metric...")
        prediction = trained_model.predict(data_x)
        prediction_proba = trained_model.predict_proba(data_x)
        
        expected_cal_error = expected_calibration_error(
            data_y, prediction_proba, prediction, len(set(data_y)), False)

        self.score = (1-expected_cal_error)