import requests
from trustML.assessment_methods.assessmentmethod import AssessmentMethod
from json import dumps

class BayesianNetwork(AssessmentMethod):
    """Class that implements the trust assessment using a Bayesian network in DNE format,
    by using a BN model previously crafted and provided in the filepath specified in the
    configuration file. It requires to have the trust metrics already computed in the trust object.

    It also requires an active and listening server with the SSI-Assessment API-library 
    deployed (https://github.com/martimanzano/SSI-assessment). Its endpoint shall be 
    specified in the configuration file.
    """

    def __init__(self, additional_properties):
        """Retrieves the set of parameters required to perform the assessment through a BN
        (including the BN filepath and discretization intervals) from the additional properties
        retrieved from the configuration file and prepares the instance's attributes to perform
        the trustworthiness assessment using the SSI assessment library.

        Args:
            additional_properties (dict): [dictionary of parameters required by the assessment method,
            i.e., the BN's filepath, endpoint of the assessment service, 
            the BN node corresponding to the trustworthiness, and the discretization intervals to use]
        
        Raises:
            Exception: When assessed metrics and BN's binning intervals are not consistent
        """

        super().__init__()

        self.BN_path = additional_properties['bn_path']
        self.API_assessment_service = additional_properties['api_url']
        self.id_trust_node = additional_properties['id_trust_node']

        self.input_nodes = additional_properties['intervals_input_nodes']        
       
    def assess(self):
        """Calls the BN assessment service synchrounously to assess the BN node with name equal to the 
        "id_trust_node" attribute. Returns the result as a JSON formatted string containing the node's 
        probabilitiies.
        """

        input_names = [k for d in self.input_nodes for k in d.keys()]
        intervals_input_nodes = [k for d in self.input_nodes for k in d.values()]

        if not self.compare_config_assesssed_metrics_inputs(input_names):
            raise Exception("Validation error in config file: assessed metrics and BN's input binning intervals mismatch")

        input_values = []
        for input_name in input_names:
            input_values.append(self.trust.get_metrics_assessment_dict()[input_name])
                   
        api_response = requests.post(url=self.API_assessment_service, 
        json={'id_si': self.id_trust_node, 'input_names': input_names,'input_values': input_values, 'intervals_input_nodes': intervals_input_nodes, 'bn_path': self.BN_path})
        
        assessment_dict = api_response.json() 
        assessment_JSON = dumps(assessment_dict)

        return assessment_dict, assessment_JSON

    def compare_config_assesssed_metrics_inputs(self, inputNames):
        """Helper function to validate the binning intervals from the configuration dict.

        Returns:
            Boolean: True if binning intervals are consistent with the assessed metrics, False otherwise
        """
        assessed_metrics_list = [metric.__class__.__name__ for metric in self.trust.metrics]
    
        if set(inputNames).issubset(set(assessed_metrics_list)):
            return True
        return False
    
    def generate_trust_PDF(self, save_path):
        """Generates a PDF containing the graphical representation of the trustworthiness assessment
        with drill-down to the assessed metrics.

        First traverses the JSON assessment to collect all the data to be plotted in the lists
        "states_names", "element_names" and "probabilities". Then it iterates through every element
        and generates a PDF page with a stacked bar chart.

        Args:
            save_path (str): filepath to the PDF to generate
        """
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.backends.backend_pdf import PdfPages

        state_names = []
        element_names = []
        probabilities = []
        
        def traverse_hierarchy(element):
            # Extract metric name
            element_name = element['siname']
            element_names.append(element_name)

            # Extract states and probabilities
            states = []
            probs = []
            for state_prob in element['probsSICategories']:
                state = state_prob['idSICategory']
                probability = state_prob['probSICategory']
                states.append(state)
                probs.append(probability)

            state_names.append(states)
            probabilities.append(probs)
            
            # Traverse the "parentNodes" list recursively
            if 'parentNodes' in element:
                for parent in element['parentNodes']:
                    traverse_hierarchy(parent)

        # Start recursive traversal from the top-level element
        data = self.trust.trust_dict
        traverse_hierarchy(data)

        # Set up the plot
        # Plot each element in a separate plot
        with PdfPages(save_path) as pdf:
            for i, element_name in enumerate(element_names):
                fig, ax = plt.subplots(figsize=(2, 5))

                # Set up the plot
                num_states = len(state_names[i])
                ind = np.arange(1)
                width = 0.2

                # Plot the stacked bar
                bottom = 0
                for j in range(num_states):
                    prob = probabilities[i][j]
                    ax.bar(ind, prob, width, bottom=bottom, label=state_names[i][j])
                    bottom += prob

                # Customize the plot
                fig.suptitle('Trustworthiness assessment - Bayesian Network', fontsize=16)

                ax.set_ylabel('Probability')
                ax.set_title("Element: " + element_name)
                ax.set_xticks([])
                ax.legend(title='States', bbox_to_anchor=(1.05, 1))

                # to switch off the horizontal axis
                frame1 = fig.gca()
                frame1.axes.get_xaxis().set_visible(False)

                pdf.savefig(fig, bbox_inches='tight')
