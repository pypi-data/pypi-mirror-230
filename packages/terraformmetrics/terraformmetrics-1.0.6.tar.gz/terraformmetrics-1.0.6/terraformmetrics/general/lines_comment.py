from terraformmetrics.lines_metric import LinesMetric

class LinesComment(LinesMetric):
    """ This class measures the number of comments in a Terraform script"""

    def count(self):
        """Return the number of commented lines
        Returns
        -------
        int
            Number of commented lines
        """
        cloc = 0

        in_multiline_comment = False
        for line in self.hcl.splitlines():
            stripped_line = line.strip()
            if not stripped_line:
                continue
            if stripped_line.startswith("#"):
                cloc += 1

            # Gestisci commenti su più linee
            if stripped_line.startswith("/*"):
                in_multiline_comment = True
                cloc += 1
                if "*/" in stripped_line:
                    in_multiline_comment = False
                    continue
                else:
                    continue
            elif "*/" in stripped_line:
                in_multiline_comment = False
                cloc += 1
                continue

            if in_multiline_comment:
                cloc += 1

        return cloc
