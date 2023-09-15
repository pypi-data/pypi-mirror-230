from terraformmetrics.lines_metric import LinesMetric


class LinesCode(LinesMetric):
    """ This class measures the number of executable lines of code in a Terraform script.
    """

    def count(self):
        """Return the number of executable lines of code.

        Returns
        -------
        int
            Number of lines of code
        """
        loc = 0
        in_multiline_comment = False
        for line in self.hcl.splitlines():
            stripped_line = line.strip()
            if not stripped_line:
                continue
            if stripped_line.startswith("#"):
                continue

            # Gestisci commenti su più linee
            if stripped_line.startswith("/*"):
                in_multiline_comment = True
                if "*/" in stripped_line:
                    in_multiline_comment = False
                    continue
                else:
                    continue
            elif "*/" in stripped_line:
                in_multiline_comment = False
                continue

            if in_multiline_comment:
                continue

            loc += 1

        return loc
