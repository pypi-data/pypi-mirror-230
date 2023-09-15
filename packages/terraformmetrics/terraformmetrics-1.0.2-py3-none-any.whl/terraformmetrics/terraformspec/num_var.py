from terraformmetrics.terraform_metric import TerraformMetric


class NumVar(TerraformMetric):
    """ This class measures the number of input vars in a Script Terraform
    """

    def count(self):
        """Return the number of input vars
        Returns
        -------
        int
            Number of input vars
        """

        # Funzione ricorsiva per contare il numero di variabili all'interno di un file
        def count_variables(data):
            count = 0

            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'variable' and isinstance(value, list):
                        for variable in value:
                            count += 1
            elif isinstance(data, list):
                for item in data:
                    count += count_variables(item)

            return count

        total_var_count = count_variables(self.tfparsed)

        return total_var_count

