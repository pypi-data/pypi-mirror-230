from terraformmetrics.terraform_metric import TerraformMetric


class NumDependsOn(TerraformMetric):
    """ This class measures the number of occurrences of the depends_on parameter
    """

    def count(self):
        """Return the number of occurrences of the depends_on parameter
        Returns
        -------
        int
             number of occurrences of the depemds_on parameter
        """
        count = 0

        def count_depends_on(data):
            counter = 0
            if isinstance(data, dict):
                counter = sum(1 for key, value in data.items() if key == "depends_on")
                for value in data.values():
                    counter += count_depends_on(value)
            elif isinstance(data, list):
                counter = sum(count_depends_on(item) for item in data)
            return counter

        num_depends = count_depends_on(self.tfparsed)
        return num_depends
