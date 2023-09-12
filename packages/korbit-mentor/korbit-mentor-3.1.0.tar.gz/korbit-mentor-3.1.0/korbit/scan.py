import json
import os
import time
from datetime import datetime
from enum import Enum

import requests

from korbit.constant import KORBIT_CODE_ANALYSIS_SERVICE, KORBIT_LOCAL_FOLDER, KORBIT_SCAN_REPORT_URL
from korbit.interface import (
    INTERFACE_SCAN_REPORT_ISSUES_COUNT_MSG,
    INTERFACE_SCAN_WAITING_REPORT_MSG,
    INTERFACE_SCAN_WAITING_START_MSG,
    INTERFACE_SLEEPING_REFRESH,
    console_print_message,
    construct_file_tree,
    create_console,
    create_progress_bar,
    generate_category_table,
)
from korbit.login import authenticate_request
from korbit.models.issue import IssueFilterThresholds
from korbit.models.report import Report, ReportCategory


class ProgressStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PROGRESS = "PROGRESS"


def display_scan_status(scan_id: int, headless=False):
    """
    Display the progress of the scan status.
    If it's headless mode, the messages will be prompt only once.
    """
    console = create_console(headless)
    previous_progress = -1
    while True:
        response = authenticate_request(requests.get, url=f"{KORBIT_CODE_ANALYSIS_SERVICE}/{scan_id}/progress")
        try:
            data = response.json()
            status = data.get("status")
            if not status:
                console_print_message(console, INTERFACE_SCAN_WAITING_START_MSG, only_once=headless)
                time.sleep(INTERFACE_SLEEPING_REFRESH)
                continue
            if status == ProgressStatus.SUCCESS.value:
                console_print_message(console, INTERFACE_SCAN_WAITING_REPORT_MSG, only_once=headless)
                break

            progress = data.get("progress", 0.0)

            title = data.get("title", "File(s) status")

            file_tree_data = data.get("files", [])
            tree = construct_file_tree(title, file_tree_data)

            progress_bar = create_progress_bar(console, f"Analyzing files ({len(file_tree_data)})...", progress)
            if headless and previous_progress == progress:
                continue
            console.clear()
            console.print(tree)
            console.print(progress_bar)

        except Exception as e:
            console.print(f"Error processing response: {e}")

        time.sleep(INTERFACE_SLEEPING_REFRESH)


def download_report(scan_id: int) -> dict:
    response = authenticate_request(
        requests.get, url=f"{KORBIT_SCAN_REPORT_URL}/{scan_id}/issues?format=json&output_concept_embedding=false"
    )
    report_path = f"{KORBIT_LOCAL_FOLDER}/{scan_id}_{datetime.now().isoformat()}_report"
    os.makedirs(KORBIT_LOCAL_FOLDER, exist_ok=True)
    html_report_path = f"{report_path}.html"
    json_report_path = f"{report_path}.json"
    with open(json_report_path, "w+") as json_file:
        issues = response.content.decode()
        json_file.write(issues)
        all_issues = json.loads(issues)
    final_issues = {}
    final_issues["issues"] = all_issues
    final_issues["scan_id"] = scan_id
    final_issues["report_path"] = html_report_path

    return final_issues


def filter_issues_by_threshold(report: Report, thresholds: IssueFilterThresholds) -> Report:
    if not thresholds:
        return report
    filtered_categories = []
    for category, issues in report.categories_iterator():
        filtered_categories.append(ReportCategory(category, thresholds.apply(issues)))

    report.categories = filtered_categories
    return report


def display_report(report: Report, headless=False) -> tuple[int, int]:
    console = create_console(headless)
    total_issues, selected_issues, ignored_issues = report.get_issues_stats()
    for i, category_issues in enumerate(report.categories):
        if not category_issues.get_total_selected_issues():
            continue

        generate_category_table(console, category_issues.category, category_issues.issues)

        if i != len(report.categories) - 1:
            console.print("\n")
            console.print("\n")

    console.print(
        INTERFACE_SCAN_REPORT_ISSUES_COUNT_MSG.format(
            total_issues=total_issues, selected_issues=selected_issues, ignored_issues=ignored_issues
        )
    )

    with open(report.report_path, "a+") as report_file:
        report_file.write(console.export_html())

    return total_issues, selected_issues
