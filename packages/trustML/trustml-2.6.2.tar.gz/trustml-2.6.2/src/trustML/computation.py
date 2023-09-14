from trustML.configreader import ConfigurationReader

class TrustComputation():
    """Class that provides the package's functionality to the endusers/systems.
    """
    def __init__(self):
        self.trust = None

    def load_trust_definition(self, config_path):
        """Loads and inicializes the required components (metrics, assessment
        method) from the provided configuration file.

        Args:
            config_path (String): Path to the configuration file
        """
        config_reader = ConfigurationReader(config_path)
        self.trust = config_reader.define_trust()

    def compute_trust(self, trained_model, data_x, data_y):
        """Performs the metrics' assessments, followed by the trust assessment
        based on such metrics and the specified assessment method and its parameters.
        Leverages this process to the trust class.

        Args:
            trained_model: classifier to evaluate
            data_x (pandas dataset): predictor data of the dataset to evaluate
            data_y (pandas dataset): target values of the dataset to evaluate
        """
        if self.trust is None:
            raise AttributeError("Trust object not defined yet")
        self.trust.assess(trained_model, data_x, data_y)

    def get_trust_as_JSON(self) -> str:
        """"""
        """Returns the trust assessment as a formated JSON string.

        Returns:
            str: trustworthiness assessment as JSON
        """
        if self.trust.trust_JSON is None:
            raise AttributeError("Trustworthiness not computed yet")
        return self.trust.trust_JSON
    
    def generate_trust_PDF(self, save_path):
        """Generates a PDF with the trust assessment graphical representation.

        Args:
            save_path (str): filepath to the PDF to generate
        
        """
        if self.trust.trust_JSON is None:
            raise AttributeError("Trustworthiness not computed yet")
        return self.trust.assessment_method.generate_trust_PDF(save_path)