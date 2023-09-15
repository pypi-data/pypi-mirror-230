from terraformmetrics.terraform_metric import TerraformMetric

import re


class NumErrorHandling(TerraformMetric):
    """ The try function is used for error handling, the method counts the number of occurrences of the latter
    """

    def count(self):
        """Return the number of try functions
        Returns
        -------
        int
            Number of try functions
        """

        # Funzione ricorsiva per contare il numero di funzioni try
        def count_try(data):
            count = 0
            if isinstance(data, dict):
                for key, value in data.items():
                    count += count_try(value)
            elif isinstance(data, list):
                for item in data:
                    count += count_try(item)
            elif isinstance(data, str):
                if re.search(r'try\(', data):
                    count += 1
            return count

        total_try_count = count_try(self.tfparsed)

        return total_try_count
