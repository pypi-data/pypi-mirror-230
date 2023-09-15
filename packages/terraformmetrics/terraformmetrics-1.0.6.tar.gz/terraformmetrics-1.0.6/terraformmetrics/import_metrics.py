#General Metrics
from terraformmetrics.general.lines_code import LinesCode
from terraformmetrics.general.lines_blank import LinesBlank
from terraformmetrics.general.lines_comment import LinesComment
from terraformmetrics.general.num_conditions import NumConditions
from terraformmetrics.general.num_decisions import NumDecisions
from terraformmetrics.general.num_tokens import NumTokens
from terraformmetrics.general.num_math_operations import NumMath
from terraformmetrics.general.text_entropy import TextEntropy

#Terraform specific
from terraformmetrics.terraformspec.num_resources import NumResources
from terraformmetrics.terraformspec.avg_resource_size import AvgResourcesSize
from terraformmetrics.terraformspec.num_remote_exec import NumRemoteExec
from terraformmetrics.terraformspec.num_file_provisioner import NumFileProvisioner
from terraformmetrics.terraformspec.num_permissions import NumFilePermissions
from terraformmetrics.terraformspec.num_modules import NumModules
from terraformmetrics.terraformspec.num_http_datasource import NumHttp
from terraformmetrics.terraformspec.num_error_handling import NumErrorHandling
from terraformmetrics.terraformspec.num_regex import NumRegex
from terraformmetrics.terraformspec.num_path import NumPath
from terraformmetrics.terraformspec.num_var import NumVar
from terraformmetrics.terraformspec.num_output import NumOutputs
from terraformmetrics.terraformspec.num_provider import NumProviders
from terraformmetrics.terraformspec.num_depends_on import NumDependsOn
from terraformmetrics.terraformspec.num_data_sources import NumDataSources
from terraformmetrics.terraformspec.num_dynamic_blocks import NumDynamicBlock
from terraformmetrics.terraformspec.num_local import NumLocals

general_metrics = {
                    'lines_code': LinesCode,
                    'lines_blank': LinesBlank,
                    'lines_comment': LinesComment,
                    'num_conditions': NumConditions,
                    'num_decisions': NumDecisions,
                    'num_math': NumMath,
                  }
tf_metrics = {
                'num_resources': NumResources,
                'avg_resources_size': AvgResourcesSize,
                'num_remote_exec_provisioner': NumRemoteExec,
                'num_file_provisioner': NumFileProvisioner,
                'num_permissions': NumFilePermissions,
                'num_modules': NumModules,
                'num_http_datasource': NumHttp,
                'num_error_handling': NumErrorHandling,
                'num_tokens': NumTokens,
                'num_regex': NumRegex,
                'num_path': NumPath,
                'num_var': NumVar,
                'num_outputs': NumOutputs,
                'num_providers': NumProviders,
                'num_depends_on': NumDependsOn,
                'num_data_sources': NumDataSources,
                'num_dynamic': NumDynamicBlock,
                'num_locals': NumLocals,
                'text_entropy' : TextEntropy,
             }

