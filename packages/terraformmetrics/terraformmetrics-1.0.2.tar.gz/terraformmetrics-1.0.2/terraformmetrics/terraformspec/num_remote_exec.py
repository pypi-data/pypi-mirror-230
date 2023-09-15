from terraformmetrics.terraform_metric import TerraformMetric


class NumRemoteExec(TerraformMetric):
    """ This class measures the number of "remote-exec" provisioner
    """

    def count(self):
        """Return the number of "remote-exec" provisioner
        Returns
        -------
        int
             number of "remote-exec" provisioner
        """
        count = 0

        def count_remote_exec_provisioners(data):
            count = 0

            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'provisioner' and isinstance(value, list):
                        for provisioner in value:
                            if isinstance(provisioner, dict):
                                for sub_key, sub_value in provisioner.items():
                                    if sub_key == 'remote-exec':
                                        count += 1
                    else:
                        count += count_remote_exec_provisioners(value)

            elif isinstance(data, list):
                for item in data:
                    count += count_remote_exec_provisioners(item)

            return count

        num_remote = count_remote_exec_provisioners(self.tfparsed)
        return num_remote
