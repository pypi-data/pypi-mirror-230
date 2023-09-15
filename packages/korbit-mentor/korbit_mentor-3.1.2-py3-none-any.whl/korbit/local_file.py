import fnmatch
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import IO, Optional
from uuid import uuid4

import requests

from korbit.constant import KORBIT_CODE_ANALYSIS_CHECK, KORBIT_LOCAL_OUTPUT_LOG_FILE
from korbit.login import authenticate_request

TEMP_FOLDER = f"{uuid4()}/"


class ZipfileEmptyError(Exception):
    pass


def compute_folder_name(_path: Path) -> str:
    if str(_path.parent).startswith(".."):
        return "parent_dir"
    elif str(_path.parent).startswith("."):
        return "current_dir"
    return f"{TEMP_FOLDER}/{_path.name}"


def compute_folder_name_for_file(_path: Path) -> str:
    folder_name = compute_folder_name(_path)
    if folder_name == _path.name:
        return str(_path.parent)
    return folder_name


def find_common_prefix(paths: list[str]) -> str:
    """Find the common prefix among the paths. If there is no common prefix, a temporary folder name is returned."""
    # If we have a single path we can still try to get the parent or folder
    common_prefix = os.path.commonprefix(paths)
    if len(paths) == 1:
        path_obj = Path(paths[0])
        if path_obj.is_file():
            common_prefix = str(path_obj.parent)
        else:
            common_prefix = path_obj.name
    # If there is no common prefix, create temporary name
    if not common_prefix:
        common_prefix = TEMP_FOLDER
    return common_prefix


def create_destination_path(temp_folder: Path, path_obj: Path, common_prefix: str) -> Path:
    """Creates a destination path based on the given temporary folder, path object, and common prefix"""
    destination_path = temp_folder / TEMP_FOLDER
    if path_obj.is_absolute():
        # Get the relative path of the file within the temporary folder
        # common_prefix will be assign to TEMP_FOLDER if there is no common prefix so we use the "/"
        rel_path = path_obj.relative_to("/" if common_prefix == TEMP_FOLDER else common_prefix)
        if str(rel_path.parent) != ".":
            destination_path /= rel_path.parent
    else:
        destination_path /= path_obj.parent
    # Create the directories in the temporary folder if they don't exist
    destination_path.mkdir(parents=True, exist_ok=True)
    return destination_path


def get_zip_top_folder_and_name(common_prefix: str) -> tuple[str, str]:
    highest_dir = os.path.basename(common_prefix.rstrip(os.sep))
    highest_dir = compute_folder_name(Path(highest_dir))
    return highest_dir, highest_dir + ".zip"


def create_temp_folder(zip_file_name: str) -> Path:
    temp_folder = Path(tempfile.gettempdir()) / zip_file_name
    temp_folder.mkdir(parents=True, exist_ok=True)
    return temp_folder


def copy_files_to_temp_folder_with_ignore(
    paths: list[str], temp_folder: Path, common_prefix: str, ignore_paths: list[str]
) -> None:
    for path in paths:
        path_obj = Path(path)
        if any(fnmatch.fnmatch(str(path_obj), pattern) for pattern in ignore_paths):
            continue
        if path_obj.is_file():
            destination_path = create_destination_path(temp_folder, path_obj, common_prefix)
            shutil.copy(path_obj, destination_path / path_obj.name)
        elif path_obj.is_dir():
            destination_path = compute_folder_name(path_obj)
            shutil.copytree(
                path_obj,
                temp_folder / destination_path,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(*ignore_paths),
            )


def create_zip_file(temp_folder: Path, zip_file_name: str, exclude_paths: list[str]) -> str:
    with zipfile.ZipFile(zip_file_name, "w") as zipf:
        for file in temp_folder.rglob("*"):
            arcname = file.relative_to(temp_folder)
            # Apply exclude rules to zip creation
            if any(fnmatch.fnmatch(str(arcname), path_rule.strip()) for path_rule in exclude_paths):
                continue
            zipf.write(file, arcname=arcname)
        if len(zipf.filelist) == 0:
            raise ZipfileEmptyError("The zip file is empty.")
    return zip_file_name


def get_korbit_ignore(paths: list[Path], exclude_paths: list[str]) -> list[str]:
    final_ignore_paths = exclude_paths
    for path in paths:
        path_obj = Path(path)
        if path_obj.is_dir():
            korbit_ignore_path = path_obj / ".korbitignore"
            if korbit_ignore_path.exists():
                with korbit_ignore_path.open("r") as file:
                    for line in file:
                        final_ignore_paths.append(line.strip())
    return final_ignore_paths


def zip_paths(paths, exclude_paths: list[str] = []):
    common_prefix = find_common_prefix(paths)
    highest_dir, zip_file_name = get_zip_top_folder_and_name(common_prefix)
    temp_folder = create_temp_folder(highest_dir)
    try:
        ignore_paths = get_korbit_ignore(paths, exclude_paths)
        copy_files_to_temp_folder_with_ignore(paths, temp_folder, common_prefix, ignore_paths)
        zip_file_name = create_zip_file(temp_folder, zip_file_name, ignore_paths)
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(temp_folder)
    return zip_file_name


def upload_file(zip_file_path: str) -> Optional[int]:
    with open(zip_file_path, "rb") as file:
        response = authenticate_request(requests.post, url=KORBIT_CODE_ANALYSIS_CHECK, files={"repository": file})
        if response.status_code == 200:
            return response.json()
        else:
            return None


def get_output_file(mode="a+") -> IO:
    return open(KORBIT_LOCAL_OUTPUT_LOG_FILE, mode)


def clean_output_file():
    if os.path.exists(KORBIT_LOCAL_OUTPUT_LOG_FILE):
        os.remove(KORBIT_LOCAL_OUTPUT_LOG_FILE)
