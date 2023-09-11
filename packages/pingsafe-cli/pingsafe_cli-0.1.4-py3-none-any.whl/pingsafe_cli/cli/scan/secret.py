import hashlib
import json
import logging
import os.path
import subprocess
import sys
import tempfile

from tabulate import tabulate
import uuid
from pingsafe_cli.cli.registry import CodeTypeSubParser, BASELINE_FILE, MissingRequiredFlags, MissingDependencies, \
    LogColors
from pingsafe_cli.cli.utils import read_from_file, get_config_path, write_json_to_file, get_version, \
    print_output_on_file, get_severity_color, get_wrapping_length, wrap_text

LOGGER = logging.getLogger("cli")
HASH_STRING = "pingsafe_hashing_string"


def print_detectors(args, detectors, global_config_data):
    required_width = get_wrapping_length(4)
    if len(detectors) > 0:
        table_data = []
        for detector in detectors:
            severity_color = get_severity_color(detector["severity"])
            table_data.append({
                "Type": detector["type"],
                "Severity": wrap_text(severity_color + detector["severity"] + LogColors.ENDC, required_width),
                "Can-Verify": wrap_text(str(detector["can_verify"]), required_width),
            })
        print(tabulate(table_data, headers="keys", tablefmt="psql"))
        print_output_on_file(args, detectors, global_config_data)
    else:
        LOGGER.info("No detectors found.")
    return 0


def secret_parser(args, cache_directory):
    secret_pre_evaluation(args)

    global_config_path = get_config_path(cache_directory)
    global_config_data = read_from_file(global_config_path)

    secret_config_path = get_config_path(cache_directory, CodeTypeSubParser.SECRET)
    secret_config_data = read_from_file(secret_config_path)

    # Calling secret-detector binary
    issues = call_secret_detector(args, global_config_data, secret_config_data, cache_directory)

    if args.generate_baseline and args.range:
        return generate_baseline(issues, args.directory)

    if args.list_detectors:
        return print_detectors(args, issues, global_config_data)

    if len(issues) > 0:
        return secret_post_evaluation(args, issues, secret_config_data, global_config_data)
    else:
        print(LogColors.OKGREEN + "RESULT\tScan completed. No issue found!" + LogColors.ENDC)
    return 0


def secret_pre_evaluation(args):
    if args.generate_baseline and (len(args.range) < 2):
        raise MissingRequiredFlags("Please provide mandatory flag --range while generating baseline.")


def generate_baseline(issues, repo_path):
    baseline_path = os.path.join(repo_path, BASELINE_FILE)

    result_hash = [generate_components_hash(issue["patches"], issue["type"]) for issue in issues]

    write_json_to_file(baseline_path, {"ignored_secrets_hash": list(set(result_hash))})
    LOGGER.info(f"Baseline generated successfully at {baseline_path}")
    return 0


def secret_post_evaluation(args, issues, secret_config_data, global_config_data):
    filtered_issues = []
    ignored_secrets_hash = []
    exit_code = 0

    baseline_path = os.path.join(args.directory, BASELINE_FILE)
    if os.path.exists(baseline_path):
        baseline_data = read_from_file(baseline_path)
        ignored_secrets_hash = baseline_data["ignored_secrets_hash"]

    for issue in issues:
        check_for_exit = False
        if args.include_ignored:
            check_for_exit = True
            filtered_issues.append(issue)
        elif generate_components_hash(issue["patches"], issue["type"]) not in ignored_secrets_hash:
            check_for_exit = True
            filtered_issues.append(issue)

        if exit_code == 0 and check_for_exit and evaluate_exit_strategy(issue, secret_config_data) == 1:
            exit_code = 1

    show_commit_id = False
    if args.all_commits or args.range or args.pull_request:
        show_commit_id = True

    if len(filtered_issues) > 0:
        # as shell is not available in pre-commit, hence not printing table on console
        if args.pre_commit and not args.quiet and not args.verbose:
            LOGGER.warning(
                "Please use --quiet/-q(recommended) or --verbose mode with pre-commit. By default, results are shown in quiet mode.")
            args.quiet = True

        print_issue_on_console(filtered_issues, args.quiet, args.verbose, show_commit_id, args.disable_verification)
        print_output_on_file(args, filtered_issues, global_config_data)
        print("RESULT\tScan completed. Found " + str(len(filtered_issues)) + " issues.")
    else:
        print(LogColors.OKGREEN + "RESULT\tScan completed. No issue found!" + LogColors.ENDC)

    return exit_code


def call_secret_detector(args, global_config_data, secret_config_data, cache_directory):
    output_file_for_secret_detector = ""
    try:
        output_file_for_secret_detector = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.json")

        command = generate_command(args, global_config_data, secret_config_data, output_file_for_secret_detector,
                                   cache_directory)
        subprocess.run(command)
        if os.path.exists(output_file_for_secret_detector):
            return read_from_file(output_file_for_secret_detector)
        return []
    except Exception as e:
        raise e
    finally:
        if os.path.exists(output_file_for_secret_detector):
            os.remove(output_file_for_secret_detector)


def generate_command(args, global_config_data, secret_config_data, output_file, cache_directory):
    workers_count = global_config_data["workers_count"]
    if args.global_workers_count:
        workers_count = args.global_workers_count

    version = get_version()
    secret_detector_binary_path = os.path.join(cache_directory, "bin", version, "bin_secret_detector")
    if not os.path.exists(secret_detector_binary_path):
        raise MissingDependencies(f"Missing bin_secret_detector {version}")

    command = [secret_detector_binary_path, "--output-path", output_file]
    if args.list_detectors:
        command.extend(["--list-detectors"])
        return command

    if len(args.directory) == 0:
        LOGGER.warning("Please provide mandatory flag -d/directory")
        sys.exit(0)

    command.extend(["--repo-path", args.directory, "--worker-count",
                    str(workers_count)])

    paths_to_skip = args.skip_paths + global_config_data["pathToIgnore"]
    excluded_detectors = get_detectors_to_exclude(secret_config_data, args.excluded_detectors)

    if args.verified_only:
        command.extend(["--verified-only"])
    if args.all_commits:
        command.extend(["--all-commits"])
    if args.pre_commit:
        command.extend(["--pre-commit"])
    if args.disable_verification:
        command.extend(["--disable-verification"])
    if len(paths_to_skip) > 0:
        for path in paths_to_skip:
            command.extend(["--skip-path", path])
    if args.range:
        command.extend(["--range", "--start", args.range[0], "--end", args.range[1]])
    if args.pull_request:
        command.extend(["--pull-request", "--start", args.pull_request[1], "--end", args.pull_request[0]])
    if len(excluded_detectors) > 0:
        for detector in excluded_detectors:
            command.extend(["--excluded-detectors", detector])
    if args.debug:
        command.extend(["--debug"])
    if args.mask_secret:
        command.extend(["--mask-secret"])

    return command


def get_detectors_to_exclude(secret_config_data, excluded_detectors):
    admin_blacklisted_detectors = []
    insuppressible_detectors = []

    if "blacklistedDetectors" in secret_config_data:
        admin_blacklisted_detectors = secret_config_data["blacklistedDetectors"]
    if "insuppressibleDetectors" in secret_config_data:
        insuppressible_detectors = secret_config_data["insuppressibleDetectors"]

    uniq_detectors_to_exclude = list(set(admin_blacklisted_detectors + excluded_detectors))

    return [detector for detector in uniq_detectors_to_exclude if detector not in insuppressible_detectors]


def generate_components_hash(secret_patches, detector_type):
    sorted_components = sorted(secret_patches.keys())
    return detector_type.lower() + "_" + calculate_hash(
        "".join(secret_patches[component]["value"] for component in sorted_components), "sha256")


def calculate_hash(string, algorithm):
    string += HASH_STRING
    hash_object = hashlib.new(algorithm)
    hash_object.update(string.encode("utf-8"))
    return hash_object.hexdigest()


def print_issue_on_console(issues, quiet, verbose, show_commit_id, is_verification_disabled):
    if verbose:
        print(json.dumps(issues, indent=4))
        return

    table_data = []
    for issue in issues:
        if quiet:
            line_numbers = [str(issue["patches"][patch]["line"]) for patch in issue["patches"].keys()]
            verified_message = "" if is_verification_disabled else "verified " if issue[
                "isSecretVerified"] else "unverified "
            message = LogColors.FAIL + f'[ISSUE]\tFound {verified_message}hardcoded {issue["title"]} at {issue["filePath"]} in line {",".join(line_numbers)}' + LogColors.ENDC
            if show_commit_id:
                message += f" for commit id {issue['commitId']}"
            print(message)
        else:
            table_data.append(generate_table_row(issue, show_commit_id, is_verification_disabled))

    if len(table_data) > 0:
        print(tabulate(table_data, headers="keys", tablefmt="psql"))


def generate_table_row(issue, show_commit_id, is_verification_disabled):
    line_numbers = [str(issue["patches"][patch]["line"]) for patch in issue["patches"].keys()]
    verification_color = LogColors.FAIL if issue["isSecretVerified"] else LogColors.WARNING
    verification_message = str(issue["isSecretVerified"])
    if is_verification_disabled:
        verification_color = LogColors.BOLD
        verification_message = "Unknown"
    severity_color = get_severity_color(issue["severity"])

    required_width = get_wrapping_length(5)
    table_data = {
        "Title": wrap_text(issue["title"], required_width),
        "Severity": wrap_text(severity_color + issue["severity"] + LogColors.ENDC, required_width),
        "Verified": wrap_text(verification_color + verification_message + LogColors.ENDC, required_width),
        "File": wrap_text(issue["filePath"], required_width),
        "Line(s)": wrap_text(",".join(line_numbers), required_width),
    }
    if show_commit_id:
        table_data["Commit Id"] = issue["commitId"]

    return table_data


def evaluate_exit_strategy(issue, secret_config_data):
    if "exitStrategy" not in secret_config_data:
        return 0

    for strategy in secret_config_data["exitStrategy"].keys():
        if strategy == "severity" and issue["severity"] not in secret_config_data["exitStrategy"]["severity"]:
            return 0
        if strategy == "exitOnlyOnVerifiedSecret" and \
                bool(secret_config_data["exitStrategy"]["exitOnlyOnVerifiedSecret"]) and not issue["isSecretVerified"]:
            return 0

    return 1
