from terraformmetrics.terraform_metric import TerraformMetric

class NumResources(TerraformMetric):
    """ This class measures the number of reources in a Script Terraform

    resources are identified by counting the number of occurrences of the keyword resource
    """

    def count(self):
        """Return the number of resources
        Returns
        -------
        int
            Number of resources
        """
        resource_list = self.tfparsed.get('resource', [])
        resource = len(resource_list)

        return resource



