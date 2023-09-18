import os
import re
import time
import json
import random

import requests
from rich import print
from rich.progress import Progress
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

from .coreutils import PROGRAM_DIRECTORY


class API:
    def __init__(self, country="US", language="en"):
        self.country = country
        self.language = language
        self.user_profile_url = "https://likee.video/@%s"
        # Likee API endpoints
        self.user_vids_endpoint = (
            "https://api.like-video.com/likee-activity-flow-micro/videoApi/getUserVideo"
        )
        self.user_info_endpoint = (
            "https://api.like-video.com/likee-activity-flow-micro/userApi/getUserInfo"
        )

        # Defining options for selenium browser
        self.browser_options = Options()
        self.browser_options.add_argument("--headless")
        self.driver = Firefox(options=self.browser_options)

    @staticmethod
    def pause(n_seconds=3):
        """
        Pauses for n_seconds. Adds a random time between 0-1
        seconds to be stochastic and avoid being blocked
        """
        time.sleep(n_seconds + random.random())

    @staticmethod
    def make_post_request(payload, endpoint, content_type="json") -> dict:
        """
        Makes a post request to the API. content_type denotes the headers to be used,
        json or url-form-encoded.

        :param payload: Payload to send together with the request
        :param endpoint: URL endpoint to send the request to.
        :param content_type: Headers to be used, json or url-form-encoded.
        :return: A JSON object containing response data if request was successful.
         An empty JSON if the request was unsuccessful.
        """
        if content_type == "json":
            response = requests.post(
                endpoint, json=payload
            )  # , headers=self.json_headers)
        else:
            response = requests.post(
                endpoint, data=payload
            )  # , headers=self.form_headers)
        # Check response has no http errors
        if response.status_code != 200:
            print("HTTP error: ", response.status_code)
            return {}
        # Convert response to json and check for error message
        response = response.json()
        if "message" in response and response["message"] != "ok":
            print("API Error: ", response["message"])
            return {}
        elif "msg" in response and response["msg"] != "success":
            print("API Error: ", response["msg"])
            return {}
        else:
            return response

    def capture_screenshot(self, username: str):
        """
        Captures a screenshot of a specified user's profile.

        :param username: Username to capture profile for.
        """
        print(f"Capturing profile screenshot ({username})... Please wait.")
        self.driver.get(self.user_profile_url % username)
        self.driver.get_screenshot_as_file(
            os.path.join(
                PROGRAM_DIRECTORY,
                username,
                "screenshots",
                f"{username}_likee-downloader.png",
            )
        )
        print(f"Screenshot captured: {username}_likee-downloader.png")

    def get_video_id(self, username: str):
        """
        Gets a video's id from a username (the author of the post).

        :param username: Author of the video/post.
        :return: A 19 digit int that represents the video's id.
        """
        self.driver.get(self.user_profile_url % username)

        # Wait for 20 seconds for an element matching the given criteria to be found
        # (wait for the page to be fully loaded)
        first_video_element = WebDriverWait(self.driver, 20).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, '//div[@class="card-video poster-bg"]')
            )
        )

        # Click on the first video and get its id
        first_video_element.click()
        video_id = self.driver.current_url[-19:]
        self.driver.quit()
        return video_id

    def get_user_id(self, username: str) -> int:
        """
        Gets a a user ID from a specified Likee username..

        :param username: username to get the ID from.
        :return: A 10 digit int representing a user's ID.
        """
        print(f"Obtaining userId ({username})... Please wait.")
        response = requests.get(
            f"{self.user_profile_url % username}/video/{self.get_video_id(username=username)}"
        )
        regex_pattern = re.compile(
            "window.data = ({.*?});", flags=re.DOTALL | re.MULTILINE
        )
        str_data = regex_pattern.search(response.text).group(1)
        json_data = json.loads(str_data)
        print(f"userId obtained: {json_data['uid']}")
        return json_data["uid"]

    def get_user_videos(
        self,
        user_id: int,
        limit: int,
        videos: list = None,
        last_post_id: int = "",
    ) -> list:
        """
        Gets a user's posted videos.

        :param user_id: User's ID.
        :param limit: Number of videos to get.
        :param last_post_id: Id of the last post.
        :param videos:
        :return: A list containing a user's videos (if available).
        """
        if videos is None:
            videos = []
        payload = {
            "country": self.country,
            "count": 100,
            "page": 1,
            "pageSize": 28,
            "lastPostId": last_post_id,
            "tabType": 0,
            "uid": user_id,
        }
        print(f"Getting {limit} videos... Please wait.")
        response = self.make_post_request(payload, self.user_vids_endpoint)
        videos.extend(response["data"]["videoList"])
        if limit:
            self.pause()
            if len(videos) < limit and len(response) > 0:
                last_id = videos[-1]["postId"]
                # Use recursion to get desired amount of videos
                return self.get_user_videos(
                    user_id, limit, last_post_id=last_id, videos=videos
                )
            else:
                return videos[:limit]

        return videos

    @staticmethod
    def download_video(video_data: dict, username: str):
        """
        Download a video to the specified user's videos directory.

        :param video_data: A JSON object containing a video's data.
        :param username: The target's username.
        """
        video_id = video_data["postId"]
        video_title = video_data["title"]

        response = requests.get(video_data["videoUrl"], stream=True)
        total_size_in_bytes = int(response.headers.get("content-length", 0))
        block_size = 1024 * 1024  # 1 Megabyte

        with Progress() as progress:
            task_id = progress.add_task(
                f"Downloading: {video_id}_{video_title}.mp4",
                total=total_size_in_bytes,
            )

            with open(
                os.path.join(
                    "likee-downloader",
                    username,
                    "videos",
                    f"{video_id}_'{video_title}'.mp4",
                ),
                "wb",
            ) as file:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        file.write(chunk)
                        progress.update(task_id, advance=len(chunk))

        print(f"Downloaded: {file.name}\n")
