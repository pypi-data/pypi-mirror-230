from typing import List

from pingsafe_cli.psgraph.common.models.enums import CheckCategories, CheckResult
from pingsafe_cli.psgraph.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GKEEnsureIntegrityMonitoring(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Integrity Monitoring for Shielded GKE Nodes is Enabled"
        check_id = "CKV_GCP_72"
        supported_resources = ['google_container_cluster', 'google_container_node_pool']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'node_config' in conf.keys():
            node = conf["node_config"][0]
            if isinstance(node, dict) and 'shielded_instance_config' in node.keys():
                monitor = node["shielded_instance_config"][0]
                if monitor.get("enable_integrity_monitoring") == [True]:
                    return CheckResult.PASSED
                return CheckResult.FAILED
            # as default is true this is a pass
            return CheckResult.PASSED
        # no config is valid it could be in the the node_pool
        return CheckResult.UNKNOWN

    def get_evaluated_keys(self) -> List[str]:
        return ["node_config/[0]/shielded_instance_config/[0]/enable_integrity_monitoring"]


check = GKEEnsureIntegrityMonitoring()
