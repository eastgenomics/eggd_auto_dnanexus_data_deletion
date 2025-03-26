#!/usr/bin/env python3
# imports
import argparse
from datetime import datetime
import json
import os
import time

from dateutil.relativedelta import relativedelta
import dxpy as dx
import pandas as pd


def get_credentials(path: str) -> str:
    """reads DNAnexus token from file

    Args:
        path (str): path to a file with DNAnexus auth token.

    Returns:
        str: DNAnexus token stripped of newline characters
    """

    with open(f"{path}", "r") as file:
        auth_token = file.read().rstrip()

    return auth_token


def dx_login(token: str):
    """Function to set authentication for DNAneuxs

    Args:
        token (str): DNAnexus token_
    """
    try:
        dx_security_context = {"auth_token_type": "Bearer", "auth_token": str(token)}

        dx.set_security_context(dx_security_context)
        print(dx.api.system_whoami())
    except dx.exceptions.InvalidAuthentication as err:
        raise dx.exceptions.InvalidAuthentication(
            f"DNAnexus Authentication failed: {err}"
        )


def find_files(project: str, older_than: int, name_pattern: str) -> list:
    """function to wrap dx api methods that can find
    tar files older than a given date in unix epoch milliseconds


    Args:
        project (str): DNAnexus project id
        older_than (int): unix epoch time in milliseconds
        name_pattern (str): regex pattern to match the file names

    Returns:
        list: contains the meta dater for each tar file found
    """
    print(f"searching {project} for files older than {older_than}s with pattern(s) {name_pattern}")
    results = list(
        dx.find_data_objects(
            project=project,
            name_mode="regexp",
            name=name_pattern,
            created_before=older_than,
            describe={
                "fields": {"name": True, "id": True, "project": True, "size": True}
            },
        )
    )
    print(f'Found {len(results)} files matching search criteria')
    return results


def file_details(files: list, patterns: list) -> pd.DataFrame:
    """a method for extracting the needed information from the file meta data


    Args:
        files (list): list of tar file metadata.
        patterns (list): list of regex patterns that was used to filter the files.

    Returns:
        pd.DataFrame: a dataframe containing the extracted meta data with a record per file found
    """
    files = [
        {
            "file": x["id"],
            "name": x["describe"]["name"],
            "project": x["project"],
            "size": x["describe"]["size"],
        }
        for x in files
    ]
    data = pd.DataFrame(files)

    for i in patterns:
        filtered_data = data[data["name"].str.contains(i)]
        print(
            f"Total size of data with pattern '{i}': {sizeof_fmt(filtered_data["size"].sum())}"
        )
    return data


def get_time_limit(months_limit: int) -> int:
    """a method to get a timestamp in unix milliseconds


    Returns:
        int: unix epoch time in miliseconds
    """
    # 15778458 is 6 months in seconds, dx uses unix epoch in milliseconds
    # 86400 ia 1 day
    now = datetime.now() - relativedelta(months=months_limit)
    limit = int(time.mktime(now.timetuple()))

    return limit * 1000


def parse_config(config_path: str) -> dict:
    """parse configuration from a json file

    Args:
        config_path (str): path to the json config file

    Returns:
        dict: configuration parameters
    """
    with open(config_path, "r") as file:
        config = json.load(file)
    return config


def sizeof_fmt(num) -> str:
    """
    Function to turn bytes to human readable file size format.

    Taken from https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size

    Parameters
    ----------
    num : int
        total size in bytes

    Returns
    -------
    str
        file size in human-readable format
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.2f}{unit}B"
        num /= 1024.0
    return f"{num:.2f}YiB"


def main():

    args = argparse.ArgumentParser()
    args.add_argument(
        "-c",
        "--config",
        type=str,
        help="Path to the configuration file",
        required=True,
    )
    args = args.parse_args()

    if not os.path.exists(args.config):
        raise ValueError(f"Configuration file path '{args.config}' does not exist")
    else:
        try:
            config = parse_config(args.config)
        except json.JSONDecodeError:
            raise ValueError(
                f"Error decoding JSON from the configuration file: {args.config}"
            )

    try:
        # assign inputs to variables
        project = config["parameters"]["project"]
        output = config["parameters"]["output"]
        file_regexs = config["parameters"]["file_regexs"]
        older_than_months = config["parameters"]["older_than_months"]
    except FileNotFoundError:
        print(f"Configuration file not found: {args.config}")
        exit(1)
    except KeyError as e:
        print(f"Missing configuration key: {e}")
        exit(1)
    
    # login to DNAnexus if running in DNAnexus app
    if os.path.exists("/home/dnanexus"):

        try:
            token_file = config["parameters"]["token_file"]
            with open(token_file, "r") as file:
                auth_token = file.read().rstrip()
                dx_login(auth_token)
        except KeyError as e:
            print(f"Missing configuration file in config: {e}")
            exit(1)
        except FileNotFoundError as e:
            print(f"Token file not found: {e}")
            exit(1)

    timelimit = get_time_limit(months_limit=older_than_months)
    details = find_files(project, timelimit, "|".join(file_regexs))

    if len(details) > 0:
        details = file_details(details, file_regexs)

        # record files for deletion
        print(
            f"Total size of data with all file types: {sizeof_fmt(details["size"].sum())}"
        )
        details.to_csv(output, header=False, index=False)
    else:
        with open(output, "w") as file:
            file.write("No files found for deletion")


if __name__ == "__main__":
    main()
