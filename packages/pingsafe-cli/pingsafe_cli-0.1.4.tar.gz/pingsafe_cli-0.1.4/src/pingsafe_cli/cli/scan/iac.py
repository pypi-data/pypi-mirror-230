import json
import logging
import os
import shutil
import subprocess
import tempfile

from tabulate import tabulate
import uuid
from collections import defaultdict
from datetime import datetime
from pingsafe_cli.cli.registry import CodeTypeSubParser, HttpMethod, TIME_FORMAT, SUPPORTED_FRAMEWORKS, \
    IacFramework, IacConfigData, MissingConfig, BASELINE_FILE, InvalidGraphConnection, LogColors, MissingDependencies, \
    DOWNLOAD_CACHE_URL, DEFAULT_PINGSAFE_DIR
from pingsafe_cli.cli.utils import make_request, read_from_file, write_json_to_file, check_if_paths_exist, wrap_text, \
    get_config_path, get_version, print_output_on_file, get_severity_color, invalidate_cache, get_wrapping_length, \
    read_file
from pingsafe_cli.psgraph.terraform.runner import Runner as TerraformRunner
from pingsafe_cli.psgraph.terraform.plan_runner import Runner as TerraformPlanRunner
from pingsafe_cli.psgraph.cloudformation.runner import Runner as CloudFormationRunner
from pingsafe_cli.psgraph.kubernetes.runner import Runner as KubernetesRunner
from pingsafe_cli.psgraph.helm.runner import Runner as HelmRunner
from pingsafe_cli.psgraph.runner_filter import RunnerFilter

from concurrent.futures import ThreadPoolExecutor

LOGGER = logging.getLogger("cli")
IAC_CONFIG_FILE = "local_config.json"
DEFAULT_FRAMEWORK_RUNNERS = {
    IacFramework.TERRAFORM: TerraformRunner(),
    IacFramework.TERRAFORM_PLAN: TerraformPlanRunner(),
    IacFramework.CLOUDFORMATION: CloudFormationRunner(),
    IacFramework.KUBERNETES: KubernetesRunner(),
    IacFramework.HELM: HelmRunner()
}


def iac_parser(args, cache_directory):
    if args.invalidate_cache:
        invalidate_cache(cache_directory)
        LOGGER.info("IaC cache invalidated!")
        return 0

    # iac_pre_evaluation make sures that iac config is present and IaC plugins are always up-to-date.
    iac_pre_evaluation(cache_directory)
    if args.list_plugins:
        return list_plugins(args, cache_directory)

    if args.directory == "":
        LOGGER.error("Missing required directory flag -d/--directory")
        return 1

    args.directory = os.path.abspath(args.directory)

    if IacFramework.ALL in args.frameworks:
        args.frameworks = DEFAULT_FRAMEWORK_RUNNERS.keys()

    results = []

    # will be used by pingsafe-iac-scanner to scan customer's custom plugins
    scan_external_plugins_dir = os.environ.get("EXTERNAL_IAC_CHECKS", "")

    for framework in args.frameworks:
        graph = DEFAULT_FRAMEWORK_RUNNERS[framework].generate_graph(args.directory,
                                                                    create_runner_filter(args, framework))

        graph_nodes = graph["nodes"]
        graph_links = graph["links"]
        if len(graph_nodes) == 0:
            continue

        grouped_nodes_by_resource_type = group_nodes_by_resource_type(graph_nodes)
        graph_nodes_by_id = get_graph_nodes_by_id(graph_nodes)
        grouped_links_by_source = group_links(graph_links, "source")
        grouped_links_by_target = group_links(graph_links, "target")
        default_plugins_framework_dir = os.path.join(cache_directory, CodeTypeSubParser.IAC, framework.upper())

        external_plugins_framework_dir = ""
        if scan_external_plugins_dir != "":
            external_plugins_framework_dir = os.path.join(scan_external_plugins_dir, framework.upper())

        all_plugins_to_scan = get_uniq_plugins(external_plugins_framework_dir, default_plugins_framework_dir)

        results = scan_plugins(all_plugins_to_scan,
                               grouped_nodes_by_resource_type,
                               grouped_links_by_source,
                               grouped_links_by_target,
                               framework,
                               graph_nodes_by_id,
                               cache_directory,
                               args.include_ignored)

    if args.generate_baseline:
        return generate_baseline(args.directory, results)

    if len(results) > 0:
        return iac_post_evaluation(args, results, cache_directory)
    else:
        print(LogColors.OKGREEN + "RESULT\tScan completed. No issue found!" + LogColors.ENDC)
    return 0


def sort_dict_by_order(data):
    sorted_data = dict(sorted(data.items(), key=lambda x: x[1].get("order", float("inf"))))
    return sorted_data


def evaluate_plugin_on_graph(plugin_data, graph_nodes, grouped_links_by_source, grouped_links_by_target, framework,
                             graph_nodes_by_id, cache_directory, include_ignored):
    iac_config_data = None
    try:
        iac_config_data = read_from_file(get_config_path(cache_directory, CodeTypeSubParser.IAC))
    except FileNotFoundError:
        pass
    results = []

    for node in graph_nodes:
        if not include_ignored and check_if_skip(plugin_data["id"], node, framework, iac_config_data):
            continue

        LOGGER.debug(f"Scanning {plugin_data['id']} for block {node['block_name_']} on file {node['file_path_']}")

        if len(plugin_data["connections"]) > 0:
            plugin_data["connections"] = sort_dict_by_order(plugin_data["connections"])
            node = generate_sub_graph(plugin_data["connections"], node, graph_nodes_by_id, grouped_links_by_source,
                                      grouped_links_by_target)

        if evaluate_rego(node, plugin_data["rego"], cache_directory):
            results.append(generate_issue_meta(node, plugin_data))

    return results


def generate_sub_graph(plugin_connections, node, graph_nodes_by_id, grouped_links_by_source, grouped_links_by_target):
    for path_to_node, keys_to_expand in plugin_connections.items():
        path_to_nodes = path_to_node.split(".")
        current_node = node
        is_expanded_list = False

        for index, path_node in enumerate(path_to_nodes[1:]):
            if path_node not in current_node:
                break
                # raise InvalidGraphConnection(f"Invalid connection node {path_node}")
            current_node = current_node[path_node]
            # checking if it is a list and already expanded
            if type(current_node) == list and len(current_node) > 0 and type(current_node[0]) != str:
                for sub_node in current_node:
                    updated_connection = ".".join(path_to_nodes[index + 1:])
                    generate_sub_graph({updated_connection: keys_to_expand}, sub_node, graph_nodes_by_id,
                                       grouped_links_by_source, grouped_links_by_target)
                is_expanded_list = True
                break

        if type(current_node) != dict:
            continue

        if is_expanded_list:
            continue

        for key in keys_to_expand["expand"]:
            if key in current_node:
                if type(current_node[key]) == dict or (
                        type(current_node[key]) == list and len(current_node[key]) > 0 and
                        type(current_node[key][0]) == dict):
                    continue
                connected_resources = get_connected_resource(key, current_node["id"], grouped_links_by_source,
                                                             graph_nodes_by_id)
                if len(connected_resources) > 0:
                    current_node[key] = connected_resources[0] if type(
                        current_node[key]) == str else connected_resources

            elif "forced" in keys_to_expand and keys_to_expand["forced"]:
                resource_type = key.split("_ids")[0]
                connected_resources = get_forced_connected_resource(resource_type, current_node["id"],
                                                                    grouped_links_by_target,
                                                                    graph_nodes_by_id)
                if len(connected_resources) > 0: current_node[key] = connected_resources

    return node


def evaluate_rego(input_json, rego, cache_directory):
    input_json_path = None
    rego_file_path = None
    try:
        input_json_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.json")
        write_json_to_file(input_json_path, input_json)

        rego_file_path = os.path.join(tempfile.gettempdir(), f"rego_script_{uuid.uuid4()}.rego")
        with open(rego_file_path, 'w') as outfile:
            outfile.write(rego)

        # change the permission to 600 (readable and writable only by the owner)
        os.chmod(input_json_path, 0o600)
        os.chmod(rego_file_path, 0o600)

        rego_evaluator_binary_path = os.path.join(cache_directory, "bin", get_version(), "bin_eval_rego")
        if not os.path.exists(rego_evaluator_binary_path):
            raise MissingDependencies(f"Missing rego_evaluator_binary: {get_version()}")

        command = [rego_evaluator_binary_path, input_json_path, rego_file_path]
        result = subprocess.run(command, stdout=subprocess.PIPE)

        if "isVulnerable:true" in result.stdout.decode():
            return True
        return False
    except Exception as e:
        raise e
    finally:
        if os.path.exists(input_json_path):
            os.remove(input_json_path)
        if os.path.exists(rego_file_path):
            os.remove(rego_file_path)


def iac_pre_evaluation(cache_directory):
    iac_cache_dir_path = os.path.join(cache_directory, CodeTypeSubParser.IAC)
    iac_config_file_path = get_config_path(cache_directory, CodeTypeSubParser.IAC)
    global_file_path = get_config_path(cache_directory)

    if not check_if_paths_exist([global_file_path, iac_cache_dir_path, iac_config_file_path]):
        raise MissingConfig("Missing required configs")

    # fetch global and iac config data
    global_config_data = read_from_file(global_file_path)
    iac_config_data = read_from_file(iac_config_file_path)

    if check_if_upsert_required(iac_config_data, global_config_data):
        log_before_download, log_after_download = generate_iac_cache_upsert_logs(iac_config_data)
        LOGGER.info(log_before_download)

        policy_version = global_config_data.get("policy_version", 1)

        download_iac_cache(iac_cache_dir_path, global_config_data["api_token"], int(policy_version))
        # updating last refreshed time
        iac_config_data[IacConfigData.LAST_REFRESHED_AT] = str(datetime.now())
        write_json_to_file(iac_config_file_path, iac_config_data)

        LOGGER.info(log_after_download)
        return


# iac_post_evaluation: Filter results on the basis of baseline and exit strategy and write result to output file
def iac_post_evaluation(args, results, cache_directory):
    filtered_results = []
    ignored_iac_hash = []
    exit_code = 0

    iac_config_file_path = get_config_path(cache_directory, CodeTypeSubParser.IAC)
    baseline_file_path = os.path.join(args.directory, BASELINE_FILE)

    if os.path.exists(baseline_file_path):
        baseline_data = read_from_file(baseline_file_path)
        ignored_iac_hash = baseline_data["ignored_iac_hash"]

    iac_config_data = read_from_file(iac_config_file_path)
    whitelisted_severity = iac_config_data["exitStrategy"]["severity"]
    check_for_exit = False

    for res in results:
        result = res["issue_meta"]
        if args.include_ignored:
            check_for_exit = True
            filtered_results.append(result)
        elif generate_unique_issue_value(res) not in ignored_iac_hash:
            check_for_exit = True
            filtered_results.append(result)

        if check_for_exit and exit_code == 0 and result["severity"] in whitelisted_severity:
            exit_code = 1

    global_config_data = read_from_file(get_config_path(cache_directory))
    if len(filtered_results) > 0:
        # as shell is not available in pre-commit, hence not printing table on console
        if args.pre_commit and not args.quiet and not args.verbose:
            LOGGER.warning(
                "Please use --quiet/-q(recommended) or --verbose mode with pre-commit. By default, results are shown in quiet mode.")
            args.quiet = True

        print_issue_on_console(filtered_results, args.quiet, args.verbose)
        print_output_on_file(args, filtered_results, global_config_data)
        print("RESULT\tScan completed. Found " + str(len(filtered_results)) + " issue(s).")
    else:
        print(LogColors.OKGREEN + "RESULT\tScan completed. No issue found!" + LogColors.ENDC)

    return exit_code


# download_iac_cache: will download all the plugins and set them under their respective framework dir
def download_iac_cache(iac_cache_dir_path, api_token, policy_version):
    response = make_request(HttpMethod.GET, DOWNLOAD_CACHE_URL, api_token)
    admin_cache_data = response.json()

    # adding iac plugins under their respective framework directory
    plugins = admin_cache_data["plugins"]
    for framework in plugins.keys():
        if framework not in SUPPORTED_FRAMEWORKS:
            raise Exception("Manipulated Data")

        framework_dir_path = os.path.join(iac_cache_dir_path, framework)

        # deleting old plugins by deleting its framework's directory(if exists)
        if os.path.exists(framework_dir_path):
            # force delete when directory contains files
            shutil.rmtree(framework_dir_path, ignore_errors=True)
        os.makedirs(framework_dir_path)

        # creating plugin files
        for plugin_data in plugins[framework]:
            # id refers to policyCode
            if policy_version == 2:
                filename = plugin_data["id"].split(":")[-1] + ".json"
            else:
                filename = plugin_data["id"].split(":")[2] + ".json"
            file_path = os.path.normpath(os.path.join(framework_dir_path, filename))

            if not file_path.startswith(framework_dir_path):
                raise Exception("Manipulated Data")

            # No need to check if file already exists as we (re)created framework directory
            write_json_to_file(file_path, plugin_data)


def check_if_skip(plugin_id_to_skip, node, framework, iac_config_data):
    if iac_config_data is not None:
        if "insuppressiblePlugins" in iac_config_data:
            if plugin_id_to_skip in iac_config_data["insuppressiblePlugins"]:
                return False

        if "blacklistedPlugins" in iac_config_data:
            if plugin_id_to_skip in iac_config_data["blacklistedPlugins"]:
                return True

    if framework == IacFramework.TERRAFORM:
        if "tags" in node and "pingsafe-skip" in node["tags"]:
            if type(node["tags"]["pingsafe-skip"]) == str and node["tags"]["pingsafe-skip"] == plugin_id_to_skip:
                LOGGER.debug(f"Skipping {plugin_id_to_skip} as per resource tags.")
                return True
            elif type(node["tags"]["pingsafe-skip"]) == list and plugin_id_to_skip in node["tags"]["pingsafe-skip"]:
                LOGGER.debug(f"Skipping {plugin_id_to_skip} as per resource tags.")
                return True

    elif framework == IacFramework.CLOUDFORMATION:
        if "Tags" in node and "pingsafe-skip" in node["Tags"] and plugin_id_to_skip in node["Tags"]["pingsafe-skip"]:
            return True

    elif framework == IacFramework.KUBERNETES or framework == IacFramework.HELM:
        if "metadata" in node and "labels" in node["metadata"] and "pingsafe-skip" in node["metadata"]["labels"] \
                and plugin_id_to_skip in node["metadata"]["labels"]["pingsafe-skip"]:
            return True

    return False


def group_nodes_by_resource_type(nodes):
    grouped_nodes = defaultdict(list)
    for node in nodes:
        if "resource_type" in node:
            grouped_nodes[node["resource_type"]].append(node)
    return grouped_nodes


def get_graph_nodes_by_id(nodes):
    nodes_by_id = defaultdict(list)
    for node in nodes:
        nodes_by_id[node["id"]] = node
    return nodes_by_id


def group_links(links, key_to_group):
    grouped_links = defaultdict(list)
    for link in links:
        grouped_links[link[key_to_group]].append(link)
    return grouped_links


def get_connected_resource(key_to_expand, source_id, grouped_links_by_source, graph_nodes_by_id):
    connected_resources = []
    for link in grouped_links_by_source[source_id]:
        if link["label"] == key_to_expand:
            connected_resources.append(graph_nodes_by_id[link["target"]])
    return connected_resources


def get_forced_connected_resource(resource_type, target_id, grouped_links_by_target, graph_nodes_by_id):
    connected_resources = []
    for link in grouped_links_by_target[target_id]:
        source_node = graph_nodes_by_id[link["source"]]
        if "resource_type" in source_node and source_node["resource_type"] == resource_type:
            connected_resources.append(source_node)
    return connected_resources


def create_runner_filter(args, framework):
    return RunnerFilter(
        framework=framework,
        download_external_modules=args.download_external_modules,
        var_files=args.var_file
    )


def list_plugins(args, cache_directory):
    global_config_data = read_from_file(get_config_path(cache_directory))
    iac_cache_dir = os.path.join(cache_directory, CodeTypeSubParser.IAC)
    all_plugins = []
    for _, frameworks, _ in os.walk(iac_cache_dir):
        for framework in frameworks:
            framework_dir = os.path.join(iac_cache_dir, framework)
            for _, _, plugins in os.walk(framework_dir):
                for plugin in plugins:
                    plugin_data = read_from_file(os.path.join(framework_dir, plugin))
                    all_plugins.append(generate_list_plugin_dict(plugin_data))
    if len(all_plugins) > 0:
        print(tabulate(all_plugins, headers="keys", tablefmt="psql"))
        print_output_on_file(args, all_plugins, global_config_data)
    else:
        LOGGER.info("No plugin found.")


def generate_issue_meta(node, plugin_data):
    start_line, end_line = get_start_and_end_line(node)
    return {
        "issue_meta": {
            # plugin_id refers to policy_code
            "plugin_id": plugin_data.get("id", ""),
            "plugin_value": plugin_data.get("id", ""),
            "severity": plugin_data.get("severity", ""),
            "description": plugin_data.get("description", ""),
            "title": plugin_data.get("title", ""),
            "issue_message": plugin_data.get("issue_message", ""),
            "impact": plugin_data.get("impact", ""),
            "info_link": plugin_data.get("info_link", ""),
            "recommended_action": plugin_data.get("recommended_action", ""),
            "block_name": node["block_name_"],
            "file_path": node["file_path_"],
            "code_start_line": start_line,
            "code_end_line": end_line,
            "code_block": generate_code_block(node["file_path_"], start_line, end_line)
        },
        "internal": {
            "rendering_breadcrumbs": node.get("rendering_breadcrumbs_", {})
        }
    }


def generate_code_block(file_path, start_line, end_line):
    try:
        file_content = read_file(os.path.abspath(file_path))
        return "\n".join(file_content.split("\n")[start_line - 1:end_line])
    except Exception as e:
        LOGGER.debug(e)
        return ""


def get_start_and_end_line(node):
    start_line = 0
    end_line = 0

    config = node.get("config_", {})
    if len(config) == 0:
        return start_line, end_line

    start_line = config.get("__startline__", 0)
    end_line = config.get("__endline__", 0)

    if start_line != 0 or end_line != 0:
        return start_line, end_line

    blocks = node.get("block_name_", "")
    if blocks == "":
        return start_line, end_line

    blocks = blocks.split(".")
    return config[blocks[0]][blocks[1]]["__start_line__"], config[blocks[0]][blocks[1]]["__end_line__"]


def generate_baseline(repo_path, results):
    baseline_path = os.path.join(repo_path, BASELINE_FILE)

    unique_issues = [generate_unique_issue_value(result) for result in results]

    write_json_to_file(baseline_path, {"ignored_iac_hash": unique_issues})
    LOGGER.info(f"Baseline generated successfully at {baseline_path}")
    return 0


def generate_unique_issue_value(result):
    source_module = result.get("internal").get("rendering_breadcrumbs", {}).get("source_module_", [])

    if len(source_module) > 0:
        uniq_name = ''.join(module["name"] for module in source_module)

        if source_module[0]["type"] == "module":
            return result["issue_meta"]["plugin_id"] + "::" + uniq_name + "::" + result["issue_meta"]["block_name"]
    return result["issue_meta"]["plugin_id"] + "::" + result["issue_meta"]["block_name"]


def generate_list_plugin_dict(plugin_data):
    required_width = get_wrapping_length(5)
    return {
        "Provider": wrap_text(plugin_data["provider"], required_width),
        "Framework": wrap_text(plugin_data["framework"], required_width),
        "Plugin Id": wrap_text(plugin_data["id"], required_width),
        "Title": wrap_text(plugin_data["title"], required_width),
        "Severity": wrap_text(plugin_data["severity"], required_width)
    }


def print_issue_on_console(issues, quiet, verbose):
    if verbose:
        print(json.dumps(issues, indent=4))
        return

    table_data = []
    for issue in issues:
        if quiet:
            print(
                LogColors.FAIL + f'[ISSUE]\tFound vulnerability inside {issue["block_name"]} for plugin id {issue["plugin_id"]}' + LogColors.ENDC)
        else:
            table_data.append(generate_table_row(issue))

    print(tabulate(table_data, headers="keys", tablefmt="psql"))


def generate_table_row(issue):
    severity_color = get_severity_color(issue["severity"])
    required_width = get_wrapping_length(5)
    return {
        "Title": wrap_text(issue["title"], required_width),
        "Severity": wrap_text(severity_color + issue["severity"] + LogColors.ENDC, required_width),
        "Block Name": wrap_text(issue["block_name"], required_width),
        "File": wrap_text(issue["file_path"], required_width),
        "Plugin Id": wrap_text(issue["plugin_id"], required_width)
    }


def check_if_upsert_required(iac_config_data, global_config_data):
    # downloading first time or after invalidated
    if iac_config_data[IacConfigData.LAST_REFRESHED_AT] is None:
        return True

    # downloading when last refreshed time has expired
    last_refreshed_at = datetime.strptime(iac_config_data[IacConfigData.LAST_REFRESHED_AT], TIME_FORMAT)
    if (datetime.now() - last_refreshed_at).total_seconds() / 3600 > global_config_data["cacheUpdateFrequency"]:
        return True

    return False


def generate_iac_cache_upsert_logs(iac_config_data):
    if iac_config_data[IacConfigData.LAST_REFRESHED_AT] is None:
        return "Downloading IAC cache...", "Successfully downloaded IAC cache!"
    return "Updating IAC cache...", "Successfully updated IAC cache!"


def scan_plugins(plugins,
                 grouped_nodes_by_resource_type,
                 grouped_links_by_source,
                 grouped_links_by_target,
                 framework,
                 graph_nodes_by_id,
                 cache_directory,
                 include_ignored):
    results = []
    workers = int(os.environ.get("WORKERS_COUNT", 10))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for plugin in plugins:
            plugin_primary_resource_type = plugin["primary_resource_type"]

            task = executor.submit(evaluate_plugin_on_graph,
                                   plugin,
                                   grouped_nodes_by_resource_type[plugin_primary_resource_type],
                                   grouped_links_by_source,
                                   grouped_links_by_target,
                                   framework,
                                   graph_nodes_by_id,
                                   cache_directory,
                                   include_ignored)

            futures.append(task)

        for future in futures:
            results += future.result()

    return results


def get_uniq_plugins(external_plugins_framework_dir, default_plugins_framework_dir):
    plugins_to_scan = {}

    if os.path.exists(external_plugins_framework_dir):
        get_plugins_data(plugins_to_scan, external_plugins_framework_dir)

    get_plugins_data(plugins_to_scan, default_plugins_framework_dir)

    return list(plugins_to_scan.values())


def get_plugins_data(plugins_to_scan, framework_dir):
    for _, _, plugins in os.walk(framework_dir):
        for plugin in plugins:
            plugin_data = read_from_file(os.path.join(framework_dir, plugin))
            # plugin_id refers to policy_code
            plugin_id = plugin_data["id"]

            if plugin_id not in plugins_to_scan:
                plugins_to_scan[plugin_id] = plugin_data
