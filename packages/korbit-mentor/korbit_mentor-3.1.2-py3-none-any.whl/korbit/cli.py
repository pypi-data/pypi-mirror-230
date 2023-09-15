import getpass
import logging
import os
import sys

import click
import git
import requests

from korbit.constant import (
    KORBIT_COMMAND_EXIT_CODE_AUTH_FAILED,
    KORBIT_COMMAND_EXIT_CODE_BRANCH_NOT_FOUND,
    KORBIT_COMMAND_EXIT_CODE_CHECK_FAILED,
    KORBIT_COMMAND_EXIT_CODE_FILE_TOO_LARGE,
    KORBIT_COMMAND_EXIT_CODE_ISSUES_FOUND_WITHIN_THRESHOLD,
    KORBIT_COMMAND_EXIT_CODE_NO_GIT_REPOSITORY,
    KORBIT_COMMAND_EXIT_CODE_UNKNOWN_ERROR,
    KORBIT_COMMAND_EXIT_CODE_UNKNOWN_GIT_COMMAND_ERROR,
    KORBIT_LOCAL_FOLDER,
)
from korbit.interface import (
    INTERFACE_AUTH_COMMAND_HELP,
    INTERFACE_AUTH_INPUT_SECRET_ID,
    INTERFACE_AUTH_INPUT_SECRET_ID_HELP,
    INTERFACE_AUTH_INPUT_SECRET_KEY,
    INTERFACE_AUTH_INPUT_SECRET_KEY_HELP,
    INTERFACE_AUTH_UNAUTHORIZED_CREDENTIALS_MSG,
    INTERFACE_CHECK_FAILED_MSG,
    INTERFACE_SCAN_COMMAND_HELP,
    INTERFACE_SCAN_EXCLUDE_PATHS_HELP,
    INTERFACE_SCAN_EXIT_CODE_HELP,
    INTERFACE_SCAN_FINAL_REPORT_FOR_HEADLESS_MSG,
    INTERFACE_SCAN_FINAL_REPORT_PATH_MSG,
    INTERFACE_SCAN_HEADLESS_OUTPUT_REPORT_HELP,
    INTERFACE_SCAN_NO_FILE_FOUND_MSG,
    INTERFACE_SCAN_PR_COMMAND_HELP,
    INTERFACE_SCAN_PR_EXIT_CODE_HELP,
    INTERFACE_SCAN_PR_GIT_BRANCH_NOT_FOUND_MSG,
    INTERFACE_SCAN_PR_GIT_COMMAND_ERROR_MSG,
    INTERFACE_SCAN_PR_NOT_GIT_REPOSITORY_MSG,
    INTERFACE_SCAN_PREPARING_FOLDER_SCAN_MSG,
    INTERFACE_SCAN_REQUESTING_A_SCAN_MSG,
    INTERFACE_SCAN_THRESHOLD_CONFIDENCE_HELP,
    INTERFACE_SCAN_THRESHOLD_PRIORITY_HELP,
    INTERFACE_SCAN_UPLOAD_FAILED_DUE_TO_SIZE_MSG,
    INTERFACE_SOMETHING_WENT_WRONG_MSG,
)
from korbit.local_file import (
    ZipfileEmptyError,
    clean_output_file,
    get_output_file,
    upload_file,
    zip_paths,
)
from korbit.login import KorbitAuthError, store_credentials
from korbit.models.issue import IssueFilterThresholds
from korbit.models.report import Report
from korbit.scan import (
    display_report,
    display_scan_status,
    download_report,
    filter_issues_by_threshold,
)
from korbit.version_control import BranchNotFound, get_diff_paths

old_stdout, old_stderr = sys.stdout, sys.stderr


@click.group()
def cli():
    pass


@cli.command("login", help=INTERFACE_AUTH_COMMAND_HELP)
@click.option("-sid", "--secret-id", "--secret_id", default=None, help=INTERFACE_AUTH_INPUT_SECRET_ID_HELP)
@click.option("-skey", "--secret-key", "--secret_key", default=None, help=INTERFACE_AUTH_INPUT_SECRET_KEY_HELP)
@click.argument("client_secret_id", required=False, type=click.STRING)
@click.argument("client_secret_key", required=False, type=click.STRING)
def login(client_secret_id, client_secret_key, secret_id, secret_key):
    if not secret_id:
        if not client_secret_id:
            secret_id = input(INTERFACE_AUTH_INPUT_SECRET_ID)
        else:
            secret_id = client_secret_id
    if not secret_key:
        if not client_secret_key:
            secret_key = getpass.getpass(INTERFACE_AUTH_INPUT_SECRET_KEY)
        else:
            secret_key = client_secret_key
    store_credentials(secret_id, secret_key)


@cli.command("scan", help=INTERFACE_SCAN_COMMAND_HELP)
@click.option(
    "--threshold-priority", type=int, default=0, required=False, help=INTERFACE_SCAN_THRESHOLD_CONFIDENCE_HELP
)
@click.option(
    "--threshold-confidence", default=0, type=int, required=False, help=INTERFACE_SCAN_THRESHOLD_PRIORITY_HELP
)
@click.option("--exit-code", is_flag=True, default=None, required=False, help=INTERFACE_SCAN_EXIT_CODE_HELP)
@click.option(
    "--headless",
    is_flag=True,
    default=None,
    required=False,
    help=INTERFACE_SCAN_HEADLESS_OUTPUT_REPORT_HELP,
)
@click.option(
    "--exclude-paths",
    type=str,
    help=INTERFACE_SCAN_EXCLUDE_PATHS_HELP,
    required=False,
    default=".git/*,**/.git/*,**/.git,node_modules/*,**/node_modules/*,**/node_modules",
)
@click.option(
    "--verbose",
    is_flag=True,
    required=False,
    default=False,
)
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def scan(paths, threshold_priority, threshold_confidence, exit_code, headless, exclude_paths, verbose):
    global old_stdout, old_stderr
    clean_output_file()
    os.makedirs(KORBIT_LOCAL_FOLDER, exist_ok=True)
    if headless:
        output_file = get_output_file()
        sys.stdout = output_file
        sys.stderr = output_file

    click.echo(INTERFACE_SCAN_PREPARING_FOLDER_SCAN_MSG.format(paths=" ".join(paths)))
    try:
        zip_file_path = zip_paths(list(paths), exclude_paths=exclude_paths.split(","))
        click.echo(zip_file_path)
        click.echo(INTERFACE_SCAN_REQUESTING_A_SCAN_MSG.format(path=zip_file_path))
        scan_id = upload_file(zip_file_path)
        if not scan_id:
            click.echo(INTERFACE_CHECK_FAILED_MSG)
            if not headless:
                return
            sys.exit(KORBIT_COMMAND_EXIT_CODE_CHECK_FAILED)

        display_scan_status(scan_id, headless)
        issues = download_report(scan_id)
        report = Report.from_json(issues)

        issue_thresholds = IssueFilterThresholds(priority=threshold_priority, confidence=threshold_confidence)
        report = filter_issues_by_threshold(report, issue_thresholds)
        display_report(report, headless=headless)

        if not report.is_successful() and exit_code:
            click.echo(INTERFACE_SCAN_FINAL_REPORT_FOR_HEADLESS_MSG.format(path=report.report_path))
            sys.exit(KORBIT_COMMAND_EXIT_CODE_ISSUES_FOUND_WITHIN_THRESHOLD)

        click.echo(INTERFACE_SCAN_FINAL_REPORT_PATH_MSG.format(path=report.report_path))
    except KorbitAuthError as e:
        if verbose:
            logging.exception(str(e))
        click.echo(str(e))
        if exit_code:
            sys.exit(KORBIT_COMMAND_EXIT_CODE_AUTH_FAILED)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [413, 400]:
            if verbose:
                logging.exception("too large file")
            click.echo(INTERFACE_SCAN_UPLOAD_FAILED_DUE_TO_SIZE_MSG)
            if exit_code:
                sys.exit(KORBIT_COMMAND_EXIT_CODE_FILE_TOO_LARGE)
        else:
            if verbose:
                logging.exception(INTERFACE_SOMETHING_WENT_WRONG_MSG)
            click.echo(INTERFACE_SOMETHING_WENT_WRONG_MSG)
            if exit_code:
                sys.exit(KORBIT_COMMAND_EXIT_CODE_UNKNOWN_ERROR)
    except ZipfileEmptyError:
        click.echo(INTERFACE_SCAN_NO_FILE_FOUND_MSG)
    except Exception:
        if verbose:
            logging.exception(INTERFACE_SOMETHING_WENT_WRONG_MSG)
        click.echo(INTERFACE_SOMETHING_WENT_WRONG_MSG)
        if exit_code:
            sys.exit(KORBIT_COMMAND_EXIT_CODE_UNKNOWN_ERROR)
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        if exit_code:
            output_file = get_output_file("r+")
            click.echo(output_file.read())


@cli.command("scan-pr", help=INTERFACE_SCAN_PR_COMMAND_HELP)
@click.option(
    "--threshold-priority", type=int, default=0, required=False, help=INTERFACE_SCAN_THRESHOLD_CONFIDENCE_HELP
)
@click.option(
    "--threshold-confidence", default=0, type=int, required=False, help=INTERFACE_SCAN_THRESHOLD_PRIORITY_HELP
)
@click.option("--exit-code", is_flag=True, default=None, required=False, help=INTERFACE_SCAN_PR_EXIT_CODE_HELP)
@click.option(
    "--headless",
    is_flag=True,
    default=None,
    required=False,
    help=INTERFACE_SCAN_HEADLESS_OUTPUT_REPORT_HELP,
)
@click.option(
    "--exclude-paths",
    type=str,
    help=INTERFACE_SCAN_EXCLUDE_PATHS_HELP,
    required=False,
    default="**/.git/*,**/.git",
)
@click.option(
    "--verbose",
    is_flag=True,
    required=False,
    default=False,
)
@click.argument(
    "repository-path",
    type=click.Path(exists=True),
    required=False,
    default=".",
)
@click.argument("compare-branch", type=str, required=False, default="origin/master")
def scan_pr(
    repository_path,
    compare_branch,
    threshold_priority,
    threshold_confidence,
    exit_code,
    headless,
    exclude_paths,
    verbose,
):
    diff_paths = []
    try:
        diff_paths = get_diff_paths(repository_path, compare_branch=compare_branch)
    except BranchNotFound as e:
        if verbose:
            logging.exception(INTERFACE_SCAN_PR_GIT_BRANCH_NOT_FOUND_MSG.format(branch=e.branch_name))
        click.echo(INTERFACE_SCAN_PR_GIT_BRANCH_NOT_FOUND_MSG.format(branch=e.branch_name))
        if exit_code:
            sys.exit(KORBIT_COMMAND_EXIT_CODE_BRANCH_NOT_FOUND)
    except git.InvalidGitRepositoryError:
        if verbose:
            logging.exception(INTERFACE_SCAN_PR_NOT_GIT_REPOSITORY_MSG)
        click.echo(INTERFACE_SCAN_PR_NOT_GIT_REPOSITORY_MSG)
        if exit_code:
            sys.exit(KORBIT_COMMAND_EXIT_CODE_NO_GIT_REPOSITORY)
    except git.GitCommandError as e:
        error_message = e.stderr.strip()
        if verbose:
            logging.exception(
                INTERFACE_SCAN_PR_GIT_COMMAND_ERROR_MSG.format(error_message=error_message, status_code=str(e.status))
            )
        click.echo(
            INTERFACE_SCAN_PR_GIT_COMMAND_ERROR_MSG.format(error_message=error_message, status_code=str(e.status))
        )
        if exit_code:
            sys.exit(KORBIT_COMMAND_EXIT_CODE_UNKNOWN_GIT_COMMAND_ERROR)
    except:
        if verbose:
            logging.exception(INTERFACE_SOMETHING_WENT_WRONG_MSG)
        click.echo(INTERFACE_SOMETHING_WENT_WRONG_MSG)
        if exit_code:
            sys.exit(KORBIT_COMMAND_EXIT_CODE_UNKNOWN_ERROR)

    if not diff_paths:
        click.echo(INTERFACE_SCAN_NO_FILE_FOUND_MSG)
        return

    scan_command_args = diff_paths
    scan_command_args += [
        f"--threshold-priority={threshold_priority}",
        f"--threshold-confidence={threshold_confidence}",
    ]
    if exit_code:
        scan_command_args.append("--exit-code")
    if headless:
        scan_command_args.append("--headless")
    if verbose:
        scan_command_args.append("--verbose")
    scan_command_args.append(f"--exclude-paths={exclude_paths}")
    scan(scan_command_args)


if __name__ == "__main__":
    cli()
