from terraformmetrics.terraform_metric import TerraformMetric


class NumOutputs(TerraformMetric):
    """ This class measures the number of outputs used
    """

    def count(self):
        """Return the number of outputs used
        Returns
        -------
        int
            Number of outputs used
        """

        num_outputs = 0

        if 'output' in self.tfparsed:
            num_outputs = len(self.tfparsed['output'])

        return num_outputs
