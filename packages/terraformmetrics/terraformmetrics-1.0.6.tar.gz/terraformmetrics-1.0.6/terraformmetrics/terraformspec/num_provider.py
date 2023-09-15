from terraformmetrics.terraform_metric import TerraformMetric


class NumProviders(TerraformMetric):
    """ This class measures the number of providers used
    """

    def count(self):
        """Return the number of providers used
        Returns
        -------
        int
            Number of providers used
        """

        num_providers = 0

        if 'provider' in self.tfparsed:
            num_providers = len(self.tfparsed['provider'])

        return num_providers
