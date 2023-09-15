from terraformmetrics.terraform_metric import TerraformMetric


class NumDataSources(TerraformMetric):
    """ This class measures the number of data sources
    """

    def count(self):
        """Return the number of data sources used
        Returns
        -------
        int
            Number of data sources used
        """

        num_data = 0

        if 'data' in self.tfparsed:
            num_data = len(self.tfparsed['data'])

        return num_data