from terraformmetrics.terraform_metric import TerraformMetric


class NumFileProvisioner(TerraformMetric):
    """ This class measures the number of "file" provisioner
    """

    def count(self):
        """Return the number of "file" provisioner
        Returns
        -------
        int
             number of "file" provisioner
        """
        count = 0

        def count_file_provisioners(data):
            count = 0

            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'provisioner' and isinstance(value, list):
                        for provisioner in value:
                            if isinstance(provisioner, dict):
                                for sub_key, sub_value in provisioner.items():
                                    if sub_key == 'file':
                                        count += 1
                    else:
                        count += count_file_provisioners(value)

            elif isinstance(data, list):
                for item in data:
                    count += count_file_provisioners(item)

            return count

        num_file = count_file_provisioners(self.tfparsed)
        return num_file