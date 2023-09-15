from terraformmetrics.terraform_metric import TerraformMetric


class NumFilePermissions(TerraformMetric):
    """ This class measures the number of occurrences of the file_permission parameter within the "file"
    provisioner block to specify the permissions of the files being copied or created
    """

    def count(self):
        """Return the number of occurrences of the file_permission parameter
        Returns
        -------
        int
             number of occurrences of the file_permission parameter
        """
        count = 0

        def count_file_permission(data):
            counter = 0

            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'provisioner' and isinstance(value, list):
                        for provisioner in value:
                            if isinstance(provisioner, dict):
                                for sub_key, sub_value in provisioner.items():
                                    if sub_key == 'file':
                                        if 'file_permission' in provisioner['file']:
                                            counter += 1
                    else:
                        counter += count_file_permission(value)

            elif isinstance(data, list):
                for item in data:
                    counter += count_file_permission(item)

            return counter

        num_file_permission = count_file_permission(self.tfparsed)
        return num_file_permission
