from dotenv import load_dotenv
import os
import requests
from json import loads
import re
import logging
import shutil

# Load environment variables
load_dotenv()

# logging
logging.basicConfig(
    filename='tmdb_errors.log',  # Name of the log file
    level=logging.ERROR,          # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log message format
)

tv_directory = '/srv/dockerdata/media_server/media/TV'
korean_directory = '/srv/dockerdata/media_server/media/Korean'  # Target directory for Korean shows
tmdb_url = "https://api.themoviedb.org/3/tv/"

# Load API key from environment variables
api_key = os.getenv('API_KEY_READ_TOKEN')

def get_original_language(tmdbid):
    """Fetch the original language for a given TMDB ID."""
    url = f"{tmdb_url}{tmdbid}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        response_json = loads(response.text)
        return response_json.get("original_language", "Unknown")
    else:
        # Log the error instead of printing
        logging.error(f"Error fetching data for TMDB ID {tmdbid}: {response.status_code}")
        return None

def find_tmdb_ids_in_directory_name(directory_name):
    """Extract TMDB ID from the directory name."""
    match = re.search(r'\[tmdbid-(\d+)\]', directory_name)
    return match.group(1) if match else None

def move_show_to_korean_directory(dir_path):
    """Move the show directory to the Korean directory."""
    if not os.path.exists(korean_directory):
        os.makedirs(korean_directory)  # Create the Korean directory if it doesn't exist
    try:
        shutil.move(dir_path, os.path.join(korean_directory, os.path.basename(dir_path)))
        print(f"Moved {dir_path} to {korean_directory}")
    except Exception as e:
        logging.error(f"Failed to move {dir_path}: {str(e)}")

def parse_directories(tv_directory):
    """Parse all directories under the given TV directory."""
    for root, dirs, _ in os.walk(tv_directory):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            tmdbid = find_tmdb_ids_in_directory_name(dir_name)
            if tmdbid:
                original_language = get_original_language(tmdbid)
                if original_language == "ko":
                    move_show_to_korean_directory(dir_path)
                elif original_language:
                    print(f"TMDB ID: {tmdbid}, Original Language: {original_language}")

# Run the parsing function
if __name__ == "__main__":
    parse_directories(tv_directory)