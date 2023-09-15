from terraformmetrics.terraform_metric import TerraformMetric


class NumModules(TerraformMetric):
    """ This class measures the number of modules used
    """

    def count(self):
        """Return the number of modules used
        Returns
        -------
        int
            Number of modules used
        """

        num_modules = 0

        if 'module' in self.tfparsed:
            num_modules = len(self.tfparsed['module'])

        return num_modules
