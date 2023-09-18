import os
import csv
import json
import argparse

import requests
from rich import print
from rich.markdown import Markdown
from rich.tree import Tree

from .__init__ import __author__, __version__, __about_me__

PROGRAM_DIRECTORY = "likee-downloader"


def notice():
    return f"""
likee-downloader v{__version__} Copyright (C) 2022-2023  {__author__}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
"""


def check_updates():
    """
    Checks the program's updates by comparing the current program version tag and the remote version tag from GitHub.
    """
    response = requests.get(
        "https://api.github.com/repos/rly0nheart/likee-downloader/releases/latest"
    ).json()
    if response["tag_name"] == __version__:
        # gnore if the program is up to date
        pass
    else:
        print(
            f"A new release is available of {PROGRAM_DIRECTORY} ({response['tag_name']}). "
            f"Run 'pip install --upgrade likee-downloader' to get the updates.\n"
        )
        release_notes = Markdown(response["body"])
        print(release_notes)
        print("\n")


def video_data_tree(video_data: dict, video_index: int):
    """
    Visualises a video's data in a treeview structure.

    :param video_data: A JSON object containing a video's data.
    :param video_index: Index of the post being visualised to a treeview.
    """
    tree = Tree(
        f"\nPost #{video_index} [bold]{video_data['title']}[/]",
        guide_style="bold bright_blue",
    )
    for video_key, video_value in video_data.items():
        tree.add(f"{video_key}: {video_value}")
        if video_key == "sound":
            pass

    if video_data["sound"]:
        sound_branch = tree.add("[bold]Sound[/]")
        for sound_key, sound_value in video_data["sound"].items():
            sound_branch.add(f"{sound_key}: {sound_value}")
    print(tree)


def path_finder(username: str):
    """
    Create a set of directories for a given user's data.

    The function creates a main directory for the user inside the 'likee-downloader' directory.
    Inside this main directory, it creates subdirectories for different types of data:
    'videos', 'screenshots', and 'json'.

    :param username: The username of the target user.
     It is used to create a personalized directory structure where data related to the user will be stored.

    Examples:
    >>> path_finder('username123')
    # This will create the following directory structure:
    # likee-downloader/username123/
    # likee-downloader/username123/videos/
    # likee-downloader/username123/screenshots/
    # likee-downloader/username123/json/
    """
    directory_list = [
        os.path.join(PROGRAM_DIRECTORY, username),
        os.path.join(PROGRAM_DIRECTORY, username, "videos"),
        os.path.join(PROGRAM_DIRECTORY, username, "screenshots"),
        os.path.join(PROGRAM_DIRECTORY, username, "csv"),
        os.path.join(PROGRAM_DIRECTORY, username, "json"),
    ]
    for directory in directory_list:
        os.makedirs(directory, exist_ok=True)


def dump_data(video_data: dict, dump_to: argparse):
    """
    Dump video data to a specified format (JSON or CSV).

    :param video_data: A JSON object containing data of a video to dump.
    :param dump_to: An argparse namespace object that contains values: 'csv' and 'json'.
    """
    video_id = video_data["postId"]
    if dump_to == "json":
        # Define the path to save the JSON file
        json_file_path = os.path.join(PROGRAM_DIRECTORY, "json", f"{video_id}.json")

        # Open the JSON file in write mode and dump the video data into it
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(video_data, json_file, indent=4, ensure_ascii=False)

        print("Data dumped:", json_file_path)
    else:  # Assume value is "csv"
        # Define the path to save the CSV file
        csv_file_path = os.path.join(PROGRAM_DIRECTORY, "csv", f"{video_id}.csv")

        # Open the CSV file in write mode
        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)

            # Write the keys of the video data dictionary as the header row of the CSV file
            writer.writerow(video_data.keys())

            # Write the values of the video data dictionary as the second row of the CSV file
            writer.writerow(video_data.values())

        print("Data dumped:", csv_file_path)


def create_parser():
    parser = argparse.ArgumentParser(
        description=f"likee-downloader — by {__author__} | {__about_me__}",
        epilog="A program for downloading videos from Likee, given a username",
    )
    parser.add_argument("username", help="username")
    parser.add_argument(
        "-s",
        "--screenshot",
        help="capture a screenshot of the target's profile",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--limit",
        help="number of videos to get (default: %(default)s)",
        default=10,
        type=int,
    )
    parser.add_argument(
        "-d",
        "--dump",
        help="dump video data to a specified file type",
        choices=["csv", "json"],
    )
    parser.add_argument(
        "-dl",
        "--download",
        help="Download all returned videos",
        action="store_true",
        dest="download",
    )
    return parser
