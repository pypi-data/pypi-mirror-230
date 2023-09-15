from terraformmetrics.terraform_metric import TerraformMetric


class NumLocals(TerraformMetric):
    """ This class measures the number of local variables
    """

    def count(self):
        """Return the number of locals
        Returns
        -------
        int
            Number of locals
        """

        # Funzione ricorsiva per contare il numero di variabili locali
        def count_local_variables(data):
            count = 0

            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "locals":
                        count += sum(1 for _ in value)
                    else:
                        count += count_local_variables(value)
            elif isinstance(data, list):
                for item in data:
                    count += count_local_variables(item)

            return count

        total_locals_count = count_local_variables(self.tfparsed)

        return total_locals_count
