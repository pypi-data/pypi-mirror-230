from terraformmetrics.lines_metric import LinesMetric


class LinesBlank(LinesMetric):
    """ This class measures the blank lines in a Terraform script"""

    def count(self):
        """Return the number of blank lines

        -------
        int
            Number of blank lines
        """
        bloc = 0

        for line in self.hcl.splitlines():
            if not line.strip():
                bloc += 1

        return bloc