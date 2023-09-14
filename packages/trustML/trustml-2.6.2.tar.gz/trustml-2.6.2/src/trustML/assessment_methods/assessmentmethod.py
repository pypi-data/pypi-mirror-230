class AssessmentMethod:
    """Assessment method class. Implemented assessment methods should inherit
    this class and implement their custom constructor and assess methods.
    """
    def __init__(self):
        """Initializes the relevant instance's parameters"""
        pass

    def assess(self) -> str:
        """Performs the trustworthiness assessment using the assessment method (child class), and returns it
        """
        pass

    def generate_trust_PDF(self, save_path):
        """(Optional) Generates a PDF containing the graphical representation of the trustworthiness assessment 
        """
        raise NotImplementedError