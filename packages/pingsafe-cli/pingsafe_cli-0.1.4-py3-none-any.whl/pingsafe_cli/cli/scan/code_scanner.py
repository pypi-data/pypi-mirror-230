import logging
import types
from pingsafe_cli.cli.registry import CodeTypeSubParser, MissingConfig, GET_CONFIG_DATA_URL, HttpMethod, \
    IacConfigData
from pingsafe_cli.cli.utils import check_if_paths_exist, make_request, read_from_file, add_global_config_file, \
    add_iac_config_file, add_secret_config_file, get_config_path, upsert_pingsafe_cli, add_vulnerability_config_file
from pingsafe_cli.cli.scan import vulnerability
from pingsafe_cli.cli.scan import iac, secret

LOGGER = logging.getLogger("cli")


def handle_scan_sub_parser(args, cache_directory):
    global_pre_evaluation(cache_directory)
    if args.code_type_sub_parser == CodeTypeSubParser.IAC:
        return iac.iac_parser(args, cache_directory)
    elif args.code_type_sub_parser == CodeTypeSubParser.SECRET:
        return secret.secret_parser(args, cache_directory)
    elif args.code_type_sub_parser == CodeTypeSubParser.VULN:
        return vulnerability.vulnerability_parser(args, cache_directory)

# global_pre_evaluation: will check we have updated pingsafe-cli and configs
def global_pre_evaluation(cache_directory):
    global_config_file_path = get_config_path(cache_directory)
    iac_config_file_path = get_config_path(cache_directory, CodeTypeSubParser.IAC)
    secret_config_file_path = get_config_path(cache_directory, CodeTypeSubParser.SECRET)

    if not check_if_paths_exist(
            [cache_directory, global_config_file_path, iac_config_file_path, secret_config_file_path]):
        raise MissingConfig("Missing required configurations")

    upsert_pingsafe_cli(cache_directory)

    global_config_data = read_from_file(global_config_file_path)

    response = make_request(HttpMethod.GET, GET_CONFIG_DATA_URL, global_config_data["api_token"],
                            {"version": global_config_data["version"]})
    if response.status_code == 304:
        LOGGER.debug("Config up to date")
        return

    update_configs(cache_directory, global_config_data, response)


def update_configs(cache_directory, global_config_data, response):
    message_before_downloading = "Downloading Configurations..."
    message_after_downloading = "Downloaded Successfully!"

    if int(global_config_data["version"]) != 0:
        message_before_downloading = "New config version available"
        message_after_downloading = "Updated Successfully!"

    LOGGER.info(message_before_downloading)

    admin_configs = response.json()

    iac_config_data = read_from_file(get_config_path(cache_directory, CodeTypeSubParser.IAC))
    iac_last_refreshed_at = None

    if IacConfigData.LAST_REFRESHED_AT in iac_config_data:
        iac_last_refreshed_at = iac_config_data[IacConfigData.LAST_REFRESHED_AT]

    add_global_config_file(types.SimpleNamespace(**global_config_data), admin_configs)
    add_iac_config_file(cache_directory, admin_configs, iac_last_refreshed_at)
    add_secret_config_file(cache_directory, admin_configs)
    add_vulnerability_config_file(cache_directory, admin_configs)

    LOGGER.info(message_after_downloading)
