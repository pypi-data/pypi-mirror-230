from math import log2

from terraformmetrics.terraform_metric import TerraformMetric

import re


class TextEntropy(TerraformMetric):
    """ This class measures the text entropy
    """

    def count(self):
        """Return the text entropy
        Returns
        -------
        float
            text entropy
        """

        def get_words(data):
            words= []
            if isinstance(data, dict):
                for key, value in data.items():
                    if key != '__start_line__' and key != '__end_line__' and key != '__len__':
                        if isinstance(value, list):
                            for item in value:
                                words.append(key)
                        else:
                            words.append(key)
                        remaining_words = get_words(value)
                        words.extend(remaining_words)
            elif isinstance(data, list):
                for item in data:
                    if data != '__start_line__' and data != '__end_line__' and data != '__len__':
                        words.extend(get_words(item))
            elif isinstance(data, str):
                if data != '__start_line__' and data != '__end_line__' and data != '__len__':
                    words.extend(str(data).split())
            return words

        words = get_words(self.tfparsed)

        words_set = set(words)

        freq = {word: words.count(word) for word in words_set}

        entropy = 0
        for word in words_set:
            p = freq[word] / len(words)
            entropy -= p * log2(p)

        return round(entropy, 2)
