from rich import print

from .api import API
from .coreutils import (
    path_finder,
    create_parser,
    dump_data,
    notice,
    check_updates,
    video_data_tree,
)


def start_downloader():
    """
    Initiate the downloader script.

    The function initializes the API with the specified country and language settings, and then parses
    the command-line arguments to get the user input. Depending on the arguments provided, it may take
    screenshots, download videos, and/or dump data to JSON or CSV files.
    """

    # Parse the command-line arguments
    args = create_parser().parse_args()

    # Print license notice
    print(notice())

    # Check for updates
    check_updates()

    # Store the username argument in a variable for easier access
    username = args.username

    # Create the necessary directories for storing user data
    path_finder(username=username)

    # Initialize the API with country and language settings
    api = API(country="US", language="en")

    # Capture a screenshot if the screenshot argument is provided
    if args.screenshot:
        api.capture_screenshot(username=username)

    # Get the user ID associated with the username
    user_id = api.get_user_id(username=username)

    # Get the user videos (up to the specified limit) and loop through them
    for video_index, video in enumerate(
        api.get_user_videos(user_id=user_id, limit=args.limit), start=1
    ):
        # Visualise video data into a tree structure
        video_data_tree(video_data=video, video_index=video_index)

        # Download the video if the download argument is provided
        if args.download:
            api.download_video(video_data=video, username=username)

        # Dump the video data to a JSON or CSV file if the dump argument is provided
        if args.dump:
            dump_data(video_data=video, dump_to=args.dump)
            