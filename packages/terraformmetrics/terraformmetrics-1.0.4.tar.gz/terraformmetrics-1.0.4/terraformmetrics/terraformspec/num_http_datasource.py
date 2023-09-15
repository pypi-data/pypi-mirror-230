from terraformmetrics.terraform_metric import TerraformMetric


class NumHttp(TerraformMetric):
    """ This class measures the number of http data source used
    """

    def count(self):
        """Return the number of http data source used
        Returns
        -------
        int
            Number of http data source used
        """

        num_http = 0

        if 'data' in self.tfparsed:
            for elem in self.tfparsed['data']:
                if 'http' in elem:
                    num_http += 1

        return num_http
