from pingsafe_cli.psgraph.common.models.enums import CheckCategories, CheckResult
from pingsafe_cli.psgraph.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ImagePullPolicyAlways(BaseResourceCheck):

    def __init__(self):
        """
        Image pull policy should be set to always to ensure you get the correct image and imagePullSecrets are correct
        Default is 'IfNotPresent' unless image tag/digest is omitted or :latest
        https://kubernetes.io/docs/concepts/configuration/overview/#container-images

        An admission controller could be used to enforce imagePullPolicy
        """
        name = "Image Pull Policy should be Always"
        id = "CKV_K8S_15"
        supported_resources = ["kubernetes_pod", "kubernetes_pod_v1",
                               "kubernetes_deployment", "kubernetes_deployment_v1"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        spec = conf.get('spec', [None])[0]
        if isinstance(spec, dict) and spec:
            evaluated_keys_path = "spec"

            template = spec.get("template")
            if template and isinstance(template, list):
                template = template[0]
                template_spec = template.get("spec")
                if template_spec and isinstance(template_spec, list):
                    spec = template_spec[0]
                    evaluated_keys_path = f'{evaluated_keys_path}/[0]/template/[0]/spec'

            containers = spec.get("container")
            if containers is None:
                return CheckResult.UNKNOWN
            for idx, container in enumerate(containers):
                if not isinstance(container, dict):
                    return CheckResult.UNKNOWN

                if container.get("image_pull_policy"):
                    if container.get("image_pull_policy")[0] == "Always":
                        break
                else:
                    if container.get("image"):
                        name = container.get("image")[0]
                        if "latest" in name:
                            break
                        if "@" in name:
                            break
                self.evaluated_keys = [f'{evaluated_keys_path}/[0]/container/[{idx}]']
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.FAILED


check = ImagePullPolicyAlways()
