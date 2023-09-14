from trustML.assessment_methods.assessmentmethod import AssessmentMethod
from anytree import Node
from anytree.exporter import JsonExporter, DictExporter
from math import isclose

class WeightedAverage(AssessmentMethod):
    """Class that implements the trust assessment using as a weighted average. It uses the weights
    and hierarchy specified in the configuration file (passed in the additional_properties constructor's
    parameter).
    
    This class is able to process multi-level hierarchies. Obviously, the weight's sum at each level 
    must add to 1 to ensure the assessment's consistency.
    """
    
    def __init__(self, additional_properties):
        """Retrieves the dict containing the hierarchical tree to use from the additional_properties 
        parameter and prepares the instance's attributes to perform the trust assessment.

        Args:
            additional_properties (dict): [dictionary of parameters required by the assessment method, 
            i.e., the hierarchical tree containing weights for each level]
        """

        super().__init__()
        self.hierarchy_tree = additional_properties
    
    def assess(self):
        """Assesses the trust as a weighted average and stores the assessment. To ensure the assessment's
        explainability and traceability, this method produces a tree containing the hierarchical assessment,
        with the raw weighted and unweighted metrics' assessments, as well as the upper levels of the hierarchy.
         
        It leverages the hierarchical tree computation to the "evaluate_tree" function. returns the result as a 
        JSON formatted string and as a dict containing the unweighted and weighted scores at each level of the tree.
        """

        trust_hiearchy_node = Node(name="Trust")

        trust_hiearchy_node.weighted_score = round(self.evaluate_tree(self.hierarchy_tree, trust_hiearchy_node), 2)

        exporter = JsonExporter(indent=2)
        assessment_JSON = exporter.export(trust_hiearchy_node)
        assessment_dict = DictExporter().export(trust_hiearchy_node)


        return assessment_dict, assessment_JSON

    def evaluate_tree(self, dict_node, hiearchy_parent_node):
        """Recursive function that validates and assesses a certain level of the trust hierarchy tree as a weighted average.
        When such level is not a leaf node, the assessment is performed recursively. When it is a leaf node, the assessment
        is performed by taking the raw metric's value (i.e., score) from the metrics' list and its weight extracted from the
        additionalProperties dict.
 
        Args:
            dict_node (dict): Current tree's level to evaluate
            hiearchy_parent_node (anytree's Node): Parent node, used to link the current evaluated node with its parent

        Raises:
            Exception: When the hierarchy's weights are not consistent, i.e., any level of the tree does not add up to 1.

        Returns:
            float: weighted score for a hierarchy level (recursively).
        """
        tree_score = node_accumulated_weight = 0
        for node in dict_node:
            node_score = node_weight = 0
            hiearchy_child_node = Node(name=node, parent=hiearchy_parent_node)
            if type(dict_node[node]) is dict:
                hiearchy_child_node.name = node.split("-")[0]
                node_weight = float(node.split("-")[1])
                hiearchy_child_node.weight = node_weight
                node_raw_score = self.evaluate_tree(dict_node[node], hiearchy_child_node)
            else:
                node_weight = dict_node[node]
                hiearchy_child_node.weight = node_weight
                node_raw_score = self.trust.get_metrics_assessment_dict()[node]
            node_score = node_weight * node_raw_score
            tree_score += node_score
            hiearchy_child_node.weighted_score = round(node_score, ndigits=2)
            hiearchy_child_node.raw_score = round(node_raw_score, ndigits=2)
            node_accumulated_weight += node_weight
        if isclose(node_accumulated_weight, 1):
            return tree_score
        else:
            raise Exception("Validation error in configuration file: weights do not add up to 1 (" + str(node_accumulated_weight) + ") in: \n" + str(dict_node))
    
    def generate_trust_PDF(self, save_path):
        """Generates a PDF containing the graphical representation of the trustworthiness assessment
        with drill-down to the assessed metrics.

        First plots a radial bar chart (through pie chart in matplotlib) with the overall 
        trustworthiness score (%). Then, it traverses the JSON assessment and plots a grouped bar
        chart for every level of the hierarchy, whith the unweighted and weighted scores.

        Args:
            save_path (str): filepath to the PDF to generate
        """
        from matplotlib.backends.backend_pdf import PdfPages
        
        data = self.trust.trust_dict

        with PdfPages(save_path) as pdf:
            self._generate_trust_radial(data, pdf)
            self._generate_group_plot(data, pdf, data['weighted_score'])

            if 'children' in data:
                for child in data['children']:
                    self._generate_group_plot(child, pdf, child['weighted_score'])

    def _generate_trust_radial(self, data, pdf):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))
        wedgeprops = {'width':0.3, 'edgecolor':'black', 'linewidth':0}
        sizes = [data['weighted_score'], 1 - data['weighted_score']]
        ax.pie(sizes, wedgeprops=wedgeprops, startangle=90, colors=['#5DADE2', '#515A5A'])
        plt.suptitle('Trustworthiness assessment', fontsize=18)
        plt.title("Weighted Average Score")
        plt.text(0, 0, f"{sizes[0]*100}%", ha='center', va='center', fontsize=42)
              
        pdf.savefig(fig)
        plt.close()

    
    def _generate_group_plot(self, data, pdf, level_score = ""):
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(figsize=(10, 6))
        
        elements = data['children']
        n_elements = len(elements)
        width = 0.35  # Width of each bar
        indices = np.arange(n_elements)

        # Plotting the weighted_score bars
        weighted_scores = [element['weighted_score'] for element in elements]
        ax.bar(indices, weighted_scores, width, label='Weighted Score')
        for i, val in enumerate(weighted_scores):
            ax.text(i, val + 0.01, f'{val:.2f}', ha='center', va='bottom')

        # Plotting the raw_score bars
        raw_scores = [element['raw_score'] for element in elements]
        ax.bar(indices + width, raw_scores, width, label='Raw Score')
        for i, val in enumerate(raw_scores):
            ax.text(i + width, val + 0.01, f'{val:.2f}', ha='center', va='bottom')

        fig.suptitle('Trustworthiness assessment - Weighted Average', fontsize=16)
        ax.set_xlabel('Dimensions/Metrics')
        ax.set_ylabel('Scores [0-1]')
        ax.set_title('Level: ' + data['name'] + " (weighted score = " + str(level_score) + ")")
        ax.set_xticks(indices + width / 2)
        ax.set_xticklabels([f"{element['name']} (Weight: {element['weight']:.2f})" for element in elements], ha='center')
        ax.legend()

        pdf.savefig(fig)
        plt.close()