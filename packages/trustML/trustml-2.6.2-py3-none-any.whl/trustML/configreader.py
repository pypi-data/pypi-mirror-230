import yaml
from trustML import assessment_methods, metrics
from trustML.trust import Trust

class ConfigurationReader():
    """Class in charge of reading the configuration file through 
    a YAML reader and performing the initial management of the metric instances
    to be assessed and their associations with the specified assessment method,
    which is also instantiated. The association is performed through an instance
    of the Trust class.

    Args:
        Singleton (Class): Singleton implementation for Python
    """
    def __init__(self, config_path):
        """Instantiates a ConfigurationReader object to retrieve and stores the required
        data from the configuration file specified.

        Args:
            config_path (str): Filepath to the configuration file
        """
        with open(config_path, mode='r') as config_file:            
            parsed_config = yaml.safe_load(config_file)
            self.read_metrics = parsed_config['metrics']
            self.read_assessment_method = parsed_config['assessment_method']

    def define_trust(self) -> Trust:
        """Instantiates the metric objects and the assessment method to be used for the trust assessment. 
        Associates the set of metrics and assessment method to a Trust object, which is returned.

        Returns:
            Trust: Instance of the Trust indicator with the instanced asessment method and metrics
            to be used for the trust computation
        """

        assessment_method_name = list(self.read_assessment_method.keys())[0]
        assessment_method_properties = self.read_assessment_method[assessment_method_name]
        assessment_method_instance = getattr(assessment_methods, assessment_method_name)(assessment_method_properties)
        instanced_metrics = []
        #({k:v for d in assessmentMethodProperties for k, v in d.items()})

        for idx, metric in enumerate(self.read_metrics):
            if type(metric) is str:
                metric_class = getattr(metrics, metric)
                metric_instance = metric_class()
            else:
                metric_class = getattr(metrics, list(metric.keys())[0])
                metric_instance = metric_class(list(metric.values())[0])            
            instanced_metrics.append(metric_instance)

        ret = Trust()
        ret.metrics = instanced_metrics
        ret.assessment_method = assessment_method_instance
        ret.assessment_method.trust = ret

        return ret