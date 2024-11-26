#!/usr/bin/env python3
# imports
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import time

import dxpy as dx


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
def find_files(project: str, older_than: int) -> list:
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
            name="^run.*.tar.gz$",
            created_before=older_than,
            describe={
                "fields": {"name": True, "id": True, "project": True, "size": True}
            },
        )
    )
    print(len(results))
    return results


##output tar file details
def tar_details(files: list) -> list:
    """a method for extracting the needed information from the tar file meta data


    Args:
        files (list): list of tar file metadata

    Returns:
        list: list where each item contains the name,
              file id and project id for a corisponding file in the input list
    """

    details = [
        f"{x['describe']['name']},{x['id']},{x['project']}, {x['describe']['size']}"
        for x in files
    ]

    return details


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


def parse_args() -> argparse.Namespace:
    """parse command line arguments


    Returns:
        namespace: input command line arguments
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--token-file", help="a file containing dx login token")

    parser.add_argument("--project", help="DNANexus project id")

    parser.add_argument(
        "--output",
        help="destination of output file containing DNANexus files to be deleted",
    )

    return parser.parse_args()


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

    args = parse_args()

    print(args.token_file)
    auth_token = get_credentials(args.token_file)
    project = args.project
    output = args.output

    dx_login(auth_token)

    # get old tar files
    timelimit = get_time_limit()
    tars = find_files(project, timelimit)

    details = tar_details(tars)

    # record files for deletion
    with open(f"{output}", "w") as file:
        for i in details:
            file.write(f"{i}\n")


if __name__ == "__main__":
    main()
