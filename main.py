"""
TMDB Korean Media Organizer

This module automates the organization of TV show directories based on their
original language. It uses The Movie Database (TMDB) API to determine the
original language of TV shows and moves directories with a Korean ('ko')
original language to a specified "Korean" directory.

Dependencies:
    - Python 3.7 or higher.
    - os: For interacting with the filesystem.
    - json: To handle JSON responses from the TMDB API.
    - re: For extracting TMDB IDs from directory names using regex.
    - logging: For logging errors and actions.
    - shutil: For moving directories.
    - requests: To send HTTP requests to the TMDB API.
    - dotenv: For loading environment variables.
    - Install required packages with: `pip install -r requirements.txt`.

Usage:
    Run this script to automatically organize TV shows with a Korean original
    language into the "Korean" directory. Ensure that the environment variable
    `API_KEY_READ_TOKEN` is set with a valid TMDB API key.

Example:
    python organize_korean_tv.py
"""
import os
from json import loads
import re
import logging
import shutil
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename='tmdb_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

TV_DIRECTORY = '/srv/dockerdata/media_server/media/TV'
KOREAN_DIRECTORY = '/srv/dockerdata/media_server/media/Korean'
TMDB_URL = "https://api.themoviedb.org/3/tv"

API_KEY = os.getenv('API_KEY_READ_TOKEN')


def get_original_language(tmdbid: str) -> str:
    """Fetch the original language for a given TMDB ID.

    Args:
        tmdbid (str): The TMDB ID of the media.

    Returns:
        str: The original language of the media.
    """

    url = f"{TMDB_URL}/{tmdbid}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.get(url, headers=headers, timeout=10)

    if 200 == response.status_code:
        response_json = loads(response.text)
        return response_json.get("original_language", "Unknown")

    logging.error("Error fetching data for TMDB ID %s: %d",
                  tmdbid, response.status_code)
    return None


def find_tmdb_ids_in_directory_name(directory_name: str) -> str:
    """Extract TMDB ID from the directory name.

    Args:
        directory_name (str): The directory name

    Returns:
        str: The TMDB ID part of the directory name.
    """
    match = re.search(r'\[tmdbid-(\d+)\]', directory_name)
    return match.group(1) if match else None


def move_show_to_korean_directory(dir_path: str) -> None:
    """Move the show directory to the Korean directory.

    Args:
        dir_path (str): The directory path.
    """
    if not os.path.exists(KOREAN_DIRECTORY):
        # Create the Korean directory if it doesn't exist
        os.makedirs(KOREAN_DIRECTORY)
    try:
        shutil.move(dir_path, os.path.join(
            KOREAN_DIRECTORY, os.path.basename(dir_path)))
        print(f"Moved {dir_path} to {KOREAN_DIRECTORY}")
    except [FileNotFoundError, PermissionError] as e:
        logging.error("Failed to move %s: %s", dir_path, str(e))


def parse_directories(tv_directory: str) -> None:
    """Parse all directories under the given TV directory.

    Args:
        tv_directory (str): The TV directory.
    """
    for root, dirs, _ in os.walk(tv_directory):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            tmdbid = find_tmdb_ids_in_directory_name(dir_name)
            if tmdbid:
                original_language = get_original_language(tmdbid)
                if original_language == "ko":
                    move_show_to_korean_directory(dir_path)
                elif original_language:
                    print(f"TMDB ID: {tmdbid}, Original Language: {
                          original_language}")


if __name__ == "__main__":
    parse_directories(TV_DIRECTORY)
