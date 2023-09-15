from terraformmetrics.lines_metric import LinesMetric


class NumTokens(LinesMetric):
    """ This class measures the numer of tokens, i.e. the number of words separated by a blank space"""

    def count(self):
        """Return the number of words separated by a blank lines

        -------
        int
            Number of words separated by a blank lines
        """
        tokens = self.hcl.split()

        # Filtra i token significativi (parole chiave, nomi di risorse, attributi)
        significant_tokens = [token for token in tokens if token.strip()]

        # Conta il numero di token significativi
        num_significant_tokens = len(significant_tokens)

        return num_significant_tokens