#!/usr/bin/env python3
# imports
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import pandas as pd
import time

import dxpy as dx
import json


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


##find tar files
def find_files(project: str, older_than: int, name_pattern: str) -> list:
    """function to wrap dx api methods that can find
    tar files older than a given date in unix epoch milliseconds


    Args:
        project (str): DNAnexus project id
        older_than (int): unix epoch time in milliseconds

    Returns:
        list: contains the meta dater for each tar file found
    """
    print(f"older than:{older_than}")
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
    print(len(results))
    return results


##output file details
def file_details(files: list) -> pd.DataFrame:
    """a method for extracting the needed information from the tar file meta data


    Args:
        files (list): list of tar file metadata

    Returns:
        list: list where each item contains the name,
              file id and project id for a corisponding file in the input list
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

    print(f"Total size of data: {sizeof_fmt(data["size"].sum())}")
    return data


##delete tar files

##check date


##get date for deletion(6 months ago)
### TODO: need a better way of adjusting this
def get_time_limit() -> int:
    """a method to get a timestamp in unix milliseconds


    Returns:
        int: unix epoch time in miliseconds
    """
    # 15778458 is 6 months in seconds, dx uses unix epoch in milliseconds
    # 86400 ia 1 day
    now = datetime.now() - relativedelta(months=6)
    limit = int(time.mktime(now.timetuple()))

    return limit * 1000


# inputs
## argumets or read from config?


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


# get/check credetials
def main():

    # Read configuration from json file
    IN_CONTAINER = os.environ.get("CONTAINER", False)

    if IN_CONTAINER:
        config_path = "/app/NGS_Tar_deletion/configs/StagingArea_config.json"
    else:
        config_path = (
            "/home/joseph/TarDeletion/NGS_Tar_deletion/configs/StagingArea_config.json"
        )
    try:
        config = parse_config(config_path)

        # assign inputs to variables
        token_file = config["peramaters"]["token_file"]
        project = config["peramaters"]["project"]
        output = config["peramaters"]["output"]
        file_regexs = config["peramaters"]["file_regexs"]
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        exit(1)
    except KeyError as e:
        print(f"Missing configuration key: {e}")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the configuration file: {config_path}")
        exit(1)

    with open(token_file, "r") as file:
        auth_token = file.read().rstrip()
        dx_login(auth_token)

    # get old tar files
    details = pd.DataFrame()
    for pattern in file_regexs:
        timelimit = get_time_limit()
        tars = find_files(project, timelimit, pattern)

        details = pd.concat([details, file_details(tars)])

    # record files for deletion
    print(
        f"Total size of data with all file types: {sizeof_fmt(details["size"].sum())}"
    )
    details.to_csv(output, header=False, index=False)


if __name__ == "__main__":
    main()
