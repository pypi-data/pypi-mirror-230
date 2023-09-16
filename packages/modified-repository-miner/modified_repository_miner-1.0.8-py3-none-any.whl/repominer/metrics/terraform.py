from terraformmetrics.import_metrics import general_metrics, tf_metrics

from .base import BaseMetricsExtractor
from repominer.filters import is_terraform_file

METRICS_TO_COMPUTE = (
                'lines_code',
                'lines_blank',
                'lines_comment',
                'num_conditions',
                'num_decisions',
                'num_math',
                'num_resources',
                'avg_resources_size',
                'num_remote_exec_provisioner',
                'num_file_provisioner',
                'num_permissions',
                'num_modules',
                'num_http_datasource',
                'num_error_handling',
                'num_tokens',
                'num_regex',
                'num_path',
                'num_var',
                'num_outputs',
                'num_providers',
                'num_depends_on',
                'num_data_sources',
                'num_dynamic',
                'num_locals',
                'text_entropy',
)


class TerraformMetricsExtractor(BaseMetricsExtractor):

    def __init__(self, path_to_repo: str, clone_repo_to: str = None, at: str = 'release'):
        super().__init__(path_to_repo, clone_repo_to, at)

    def get_product_metrics(self, script: str) -> dict:
        """ Extract source code metrics from a script.
        It uses Terraform to compute the metrics (https://github.com/GerardoBrescia/radon-terraform-metrics)

        Parameters
        ----------
        script : str
            The content of the script to extract metrics from.

        Returns
        -------
        Dict[str, Any]
            A dictionary of <metric, value>.

        """
        results = {}

        metrics = general_metrics
        metrics.update(tf_metrics)

        for name in metrics:

            if name not in METRICS_TO_COMPUTE:
                continue

            try:
                results[name] = metrics[name](script).count()
            except TypeError:
                continue

        return results

    def ignore_file(self, path_to_file: str, content: str = None):
        return not is_terraform_file(path_to_file)