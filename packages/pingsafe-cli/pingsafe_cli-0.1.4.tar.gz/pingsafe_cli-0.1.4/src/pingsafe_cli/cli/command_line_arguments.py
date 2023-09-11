import argparse
from pingsafe_cli.cli.registry import OutputFormat, DEFAULT_PINGSAFE_DIR, GLOBAL_EPILOG, SCAN_EPILOG, CONFIG_EPILOG, \
    IAC_EPILOG, SECRET_EPILOG, VULN_EPILOG
from pingsafe_cli.cli.utils import get_home_path, get_version


def evaluate_command_line_arguments():
    # Initialize global parser
    parser = argparse.ArgumentParser(
        prog='PingSafeCli',
        description='PingSafe CLI to scan code for vulnerabilities.',
        epilog=GLOBAL_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    add_global_flags(parser)
    scan_sub_parser, config_sub_parser = add_global_sub_parser(parser)

    # Initialized subparser for code parser
    iac_parser, secret_parser, vulnerability_parser = add_scan_sub_parser(scan_sub_parser)

    # pingsafe-cli code iac ...
    add_iac_flags(iac_parser)

    # pingsafe-cli code secret ...
    add_secret_flags(secret_parser)

    # pingsafe-cli code vuln ...
    add_vulnerability_flags(vulnerability_parser)

    # pingsafe-cli config ...
    add_config_flags(config_sub_parser)

    return parser.parse_args()


def add_global_flags(parser):
    # pingsafecli --all-sub-flags... (global flags)
    parser.add_argument("--debug", dest="debug", action="store_true", default=False, help="switch to debug mode")
    parser.add_argument("--disable-sentry", dest="disable_sentry", default=False, action="store_true",
                        help="disable sentry monitoring")
    parser.add_argument("--output-file", dest="global_output_file", metavar="", default="",
                        help="output file path")
    parser.add_argument("--output-format", dest="global_output_format", metavar="",
                        help="output format", choices=[OutputFormat.JSON, OutputFormat.CSV])
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true", default=False,
                        help="show limited information")
    parser.add_argument("-v", "--version", action="version", help="pingsafe-cli version",
                        version=get_version())
    parser.add_argument("--verbose", dest="verbose", action="store_true", default=False,
                        help="show more information")
    parser.add_argument("--workers-count", dest="global_workers_count", metavar="",
                        help="worker count for concurrency")


def add_iac_flags(iac_parser):
    iac_parser.add_argument("-d", "--directory", dest="directory", default="", metavar="", help="directory to scan")
    iac_parser.add_argument("--download-external-modules", dest="download_external_modules", action="store_true",
                            default=True, help="download external modules used in code to scan")
    iac_parser.add_argument("--frameworks", dest="frameworks", nargs='+', default=["all"],
                            choices=["all", "terraform", "cloudformation", "kubernetes", "helm"],
                            metavar="", help="infrastructure as a code frameworks")
    iac_parser.add_argument("--generate-baseline", dest="generate_baseline", action="store_true", default=False,
                            help="generate baseline to ignore issues")
    iac_parser.add_argument("--include-ignored", dest="include_ignored", action="store_true", default=False,
                            help="include ignored resources from baseline and exception management")
    iac_parser.add_argument("--invalidate-cache", dest="invalidate_cache", action="store_true", default=False,
                            help="delete all stored iac cache")
    iac_parser.add_argument("--list-plugins", dest="list_plugins", action="store_true", default=False,
                            help="list all plugins")
    iac_parser.add_argument("--pre-commit", dest="pre_commit", action="store_true", default=False,
                            help="scan pre-commit changes")
    iac_parser.add_argument("--var-file", dest="var_file", nargs="+", default=[], metavar="",
                            help="variables file path")


def add_secret_flags(secret_parser):
    secret_parser.add_argument("--all-commits", dest="all_commits", action="store_true", default=False,
                               help="scan entire commit history")
    secret_parser.add_argument("-d", "--directory", dest="directory", help="directory to scan", metavar="", default="",
                               required=False)
    secret_parser.add_argument("--disable-verification", dest="disable_verification", action="store_true",
                               default=False, help="disable verification of detected secrets")
    secret_parser.add_argument("--excluded-detectors", dest="excluded_detectors", metavar="", nargs="+", default=[],
                               help="detectors to be ignored during scan")
    secret_parser.add_argument("--generate-baseline", dest="generate_baseline", action="store_true", default=False,
                               help="generate baseline to ignore issues (available only for range scan)")
    secret_parser.add_argument("--include-ignored", dest="include_ignored", action="store_true", default=False,
                               help="include ignored secrets from baseline")
    secret_parser.add_argument("--list-detectors", dest="list_detectors", action="store_true", default=False,
                               help="list of all supported detectors")
    secret_parser.add_argument("--mask-secret", dest="mask_secret", action="store_true", default=False,
                               help="mask secret in output")
    secret_parser.add_argument("--pre-commit", dest="pre_commit", action="store_true", default=False,
                               help="scan pre-commit changes")
    secret_parser.add_argument("--pull-request", dest="pull_request", nargs=2, type=str, metavar="", default=[],
                               help="scan pull request <src_branch dest_branch>")
    secret_parser.add_argument("--range", dest="range", nargs=2, type=str, metavar="", default=[],
                               help="scan range of commits <start-ref end-ref>")
    secret_parser.add_argument("--skip-paths", dest="skip_paths", nargs="+", default=[], metavar="",
                               help="paths to be ignored during scan")
    secret_parser.add_argument("--verified-only", dest="verified_only", action="store_true", default=False,
                               help="give results for verified secrets only")


def add_vulnerability_flags(vulnerability_parser):
    vulnerability_parser.add_argument("-d", "--directory", dest="directory", metavar="", default="",
                                      help="directory to scan for vulnerabilities")
    vulnerability_parser.add_argument("--docker-image", dest="docker_image", metavar="", default="",
                                      help="docker image to scan for vulnerabilities")
    vulnerability_parser.add_argument("--fixed-only", dest="only_fixed", action="store_true", default=False,
                                      help="ignore vulnerabilities for which fix/patch is not available yet!")
    vulnerability_parser.add_argument("--generate-sbom", dest="generate_sbom", action="store_true", default=False,
                                      help="generate SBOM(software bill of materials)")
    vulnerability_parser.add_argument("--password", dest="password", metavar="", default="",
                                      help="specify password/auth-token for registry")
    vulnerability_parser.add_argument("--platform", dest="platform", metavar="", default="linux/arm64",
                                      help="specify image platform (default: linux/arm64)")
    vulnerability_parser.add_argument("--registry", dest="registry", metavar="", default="index.docker.io",
                                      help="specify registry for image (default: index.docker.io)")
    vulnerability_parser.add_argument("--sbom-format", dest="sbom_format", metavar="",
                                      choices=["pingsafe-json", "cyclonedx-json", "spdx-json"],
                                      help="sbom output format, options=[pingsafe-json, cyclonedx-json, spdx-json] ("
                                           "default=pingsafe-json)")
    vulnerability_parser.add_argument("--username", dest="username", metavar="", default="",
                                      help="specify username for registry")
    vulnerability_parser.add_argument("--vuln-format", dest="vuln_format", default="pingsafe-json", metavar="",
                                      choices=["pingsafe-json", "defect-dojo-generic-format"],
                                      help="vulnerability scan export format, options=[pingsafe-json, "
                                           "defect-dojo-generic-format] ("
                                           "default=pingsafe-json)")


def add_config_flags(config_sub_parser):
    config_sub_parser.add_argument("--api-token", dest="api_token", required=True,
                                   help="api-token for pingsafe-cli")
    config_sub_parser.add_argument("--cache-directory", dest="cache_directory", metavar="",
                                   default=get_home_path(DEFAULT_PINGSAFE_DIR),
                                   help=f"pingsafe-cli cache dir (default='{get_home_path(DEFAULT_PINGSAFE_DIR)}')")
    config_sub_parser.add_argument("--output-format", dest="output_format", metavar="",
                                   help="output format for results",
                                   default=OutputFormat.JSON, choices=[OutputFormat.JSON, OutputFormat.CSV])
    config_sub_parser.add_argument("--output-file", dest="output_file", metavar="", default="",
                                   help="output file location")
    config_sub_parser.add_argument("--workers-count", dest="workers_count", default=5, metavar="",
                                   help="worker count for concurrency")
    config_sub_parser.add_argument("--on-crash-exit-code", dest="on_crash_exit_code", default=1,
                                   metavar="", type=int,
                                   help="Exit status when something went wrong")


def add_global_sub_parser(parser):
    # Initialized subparser for global parser
    sub_parser = parser.add_subparsers(dest="main_sub_parser", title="Sub Commands",
                                       description="Use following sub-commands to configure PingSafe CLI or scan your code.",
                                       help="Description")

    # pingsafe-cli subcommand[scan/config]
    scan_sub_parser = sub_parser.add_parser("scan",
                                            prog="Code Scanner",
                                            description="PingSafe CLI scan sub-command allows three types of scan(iac, secret and vuln)",
                                            help="code scanner",
                                            epilog=SCAN_EPILOG,
                                            formatter_class=argparse.RawDescriptionHelpFormatter
                                            )
    config_sub_parser = sub_parser.add_parser("config",
                                              prog="Configure PingSafe CLI",
                                              description="Configure your PingSafe CLI",
                                              help="configure pingsafe cli",
                                              epilog=CONFIG_EPILOG,
                                              formatter_class=argparse.RawDescriptionHelpFormatter
                                              )

    return scan_sub_parser, config_sub_parser


def add_scan_sub_parser(scan_sub_parser):
    sub_parser = scan_sub_parser.add_subparsers(dest="code_type_sub_parser", help="Scan Type")
    iac_parser = sub_parser.add_parser("iac",
                                       prog="IaC",
                                       description="PingSafe CLI detects misconfigurations in your IaC repository.",
                                       help="Infrastructure as a Code Scanning",
                                       epilog=IAC_EPILOG,
                                       formatter_class=argparse.RawDescriptionHelpFormatter
                                       )
    secret_parser = sub_parser.add_parser("secret",
                                          prog="Secret Detection",
                                          description="PingSafe CLI detects secrets present in your repository.",
                                          help="Secret Detection",
                                          epilog=SECRET_EPILOG,
                                          formatter_class=argparse.RawDescriptionHelpFormatter
                                          )
    vulnerability_parser = sub_parser.add_parser("vuln",
                                                 prog="Vulnerability Scanner and SBOM generator",
                                                 description="PingSafe CLI detects vulnerable dependencies and generates SBOM used in your repository/image.",
                                                 help="Vulnerability Scanner and SBOM generator",
                                                 epilog=VULN_EPILOG,
                                                 formatter_class=argparse.RawDescriptionHelpFormatter
                                                 )
    return iac_parser, secret_parser, vulnerability_parser
