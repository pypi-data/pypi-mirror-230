import re
from terraformmetrics.terraform_metric import TerraformMetric

COMPARISON_OPERATORS = re.compile(r'\bcontains\b|\bin\b|(?<= )==(?= )|(?<= )!=(?= )|(?<= )>=(?= )|(?<= )>(?= )|(?<= )<=(?= )|(?<= )<(?= )')


class NumConditions(TerraformMetric):
    """ This class measures the number of conditions within an if block in a Script Terraform

    conditions are identified by counting the number of occurrences of the operators : (== != >= > <= < in contains)
    within an if block
    """

    def count(self):
        """Return the number of conditions
        Returns
        -------
        int
            Number of conditions
        """

        # Funzione ricorsiva per contare operatori all'interno di un dizionario o una lista
        def count_operators(data):
            count = 0
            if isinstance(data, dict):
                for key, value in data.items():
                    count += count_operators(value)
            elif isinstance(data, list):
                for item in data:
                    count += count_operators(item)
            elif isinstance(data, str):
                if re.search(r' \? ', data) and re.search(r' : ', data):
                    no_quotes_text = re.sub(r'"(.*?)"', ' ', data)
                    count += len(COMPARISON_OPERATORS.findall(str(no_quotes_text)))
            return count

        total_operator_count = count_operators(self.tfparsed)

        return total_operator_count
