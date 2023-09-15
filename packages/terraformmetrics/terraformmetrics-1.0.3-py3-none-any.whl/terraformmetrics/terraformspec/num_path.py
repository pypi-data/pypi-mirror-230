import re
from terraformmetrics.terraform_metric import TerraformMetric

PATH_REGEX = re.compile(r'\b[\w/.-]+(?:/+[\w/.-]*)+\b')


class NumPath(TerraformMetric):
    """ This class measures the number of paths in a Script Terraform
    """

    def count(self):
        """Return the number of paths
        Returns
        -------
        int
            Number of paths
        """

        # Funzione ricorsiva per contare il numero di path all'interno di un file
        def count_paths(data):
            count = 0
            if isinstance(data, dict):
                for key, value in data.items():
                    count += count_paths(value)
            elif isinstance(data, list):
                for item in data:
                    count += count_paths(item)
            elif isinstance(data, str):
                path_matches = PATH_REGEX.findall(data)
                ip_matches = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}\b', data)
                filtered_matches = [match for match in path_matches if match not in ip_matches]
                count += len(filtered_matches)
            return count

        total_paths_count = count_paths(self.tfparsed)

        return total_paths_count
    