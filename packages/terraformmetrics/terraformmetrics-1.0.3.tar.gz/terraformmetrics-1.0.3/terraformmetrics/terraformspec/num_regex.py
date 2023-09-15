from terraformmetrics.terraform_metric import TerraformMetric

import re


class NumRegex(TerraformMetric):
    """ This class measures the number of regex used, counting the number of regex and regexall functions
    """

    def count(self):
        """Return the number of regex or regexall functions
        Returns
        -------
        int
            Number of regex or regexall
        """

        # Funzione ricorsiva per contare il numero di funzioni regex o regexall
        def count_regex(data):
            count = 0
            if isinstance(data, dict):
                for key, value in data.items():
                    count += count_regex(value)
            elif isinstance(data, list):
                for item in data:
                    count += count_regex(item)
            elif isinstance(data, str):
                if re.search(r'regex\(', data) or re.search(r'regexall\(', data):
                    count += 1
            return count

        total_regex_count = count_regex(self.tfparsed)

        return total_regex_count
