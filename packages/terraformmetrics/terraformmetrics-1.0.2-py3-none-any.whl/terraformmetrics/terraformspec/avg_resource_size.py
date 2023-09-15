from terraformmetrics.terraform_metric import TerraformMetric


class AvgResourcesSize(TerraformMetric):
    """ This class measures the average number of lines of code of resources
    """

    def count(self):
        """Return the average resource size
        Returns
        -------
        int
            Average resource size, rounded to the nearest unit
        """

        def find_start_end_lines(d):
            if isinstance(d, dict):
                if '__start_line__' in d and '__end_line__' in d:
                    return d['__start_line__'], d['__end_line__']
                for value in d.values():
                    lines = find_start_end_lines(value)
                    if lines:
                        return lines
            return None

        total_resources_lines = 0
        avg_resource_size = 0

        resource_list = self.tfparsed.get('resource', [])
        for resource in resource_list:
            start_line, end_line = find_start_end_lines(resource)

            empty_line_count = 0

            for line_number, line in enumerate(self.tfscript, start=1):
                if start_line <= line_number <= end_line:
                    if not line.strip():
                        empty_line_count += 1

            total_lines = end_line - start_line + 1
            source_lines = total_lines - empty_line_count

            total_resources_lines += source_lines
        if len(resource_list) != 0:
            avg_resource_size = int(round(total_resources_lines/len(resource_list)))
        return avg_resource_size
