import tweepy
import os
import glob
import sys
import time
from datetime import datetime

X_API_KEY = os.getenv("X_API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET =os.getenv("ACCESS_TOKEN_SECRET") 

TARGET_DIRECTORY = "."

def get_api_client():
    """Authenticates with the X API and returns a client object."""
    # Check if the environment variables are set
    if not all([X_API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print("🛑 Error: One or more required environment variables are not set.")
        print("   Please set API_KEY, API_SECRET_KEY, ACCESS_TOKEN, and ACCESS_TOKEN_SECRET.")
        return None

    try:
        client = tweepy.Client(
            consumer_key=X_API_KEY,
            consumer_secret=API_SECRET_KEY,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        print("✅ Successfully authenticated with X API.")
        return client
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return None

def find_most_recent_file(directory):
    """
    Finds the most recent file based on the timestamp in its filename.
    Assumes filename format is 'Response_YYYY-MM-DD_HH-MM-SS.txt'.
    """
    try:
        # Create a pattern to find all response files
        search_pattern = os.path.join(directory, 'Response_*.txt')
        
        # Get a list of all files matching the pattern
        files = glob.glob(search_pattern)
        
        if not files:
            print(f"🤔 No files with format 'Response_*.txt' found in the directory: {os.path.abspath(directory)}")
            return None
        
        latest_file = None
        latest_time = None
        
        # Define the timestamp format
        # Corresponds to "%Y-%m-%d_%H-%M-%S"
        time_format = "%Y-%m-%d_%H-%M-%S"

        for file_path in files:
            try:
                # Extract the filename from the full path
                filename = os.path.basename(file_path)
                # Extract the timestamp part of the filename
                # It's between "Response_" and ".txt"
                timestamp_str = filename.replace("Response_", "").replace(".txt", "")
                
                # Convert the string to a datetime object
                file_time = datetime.strptime(timestamp_str, time_format)
                
                # Compare with the latest time found so far
                if latest_time is None or file_time > latest_time:
                    latest_time = file_time
                    latest_file = file_path
            except ValueError:
                # This will catch files that match the glob pattern but not the timestamp format
                print(f"⚠️ Skipping file with incorrect format: {filename}")
                continue

        if latest_file:
            print(f"📄 Found most recent file: {latest_file}")
        
        return latest_file
        
    except Exception as e:
        print(f"❌ Error finding files: {e}")
        return None

def read_file_content(filepath):
    """Reads the content of a file using UTF-8 encoding to support emojis."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print("⚠️ The file is empty. Nothing to post.")
                return None
            print("📜 Content read from file.")
            return content
    except FileNotFoundError:
        print(f"❌ Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def post_to_x(client, text_to_post):
    """Posts the given text to the authenticated X account."""
    if not client or not text_to_post:
        return

    try:
        print("⏳ Posting to X...")
        response = client.create_tweet(text=text_to_post)
        print(f"✅ Successfully posted! Tweet ID: {response.data['id']}")
        print(f"🔗 View it here: https://twitter.com/user/status/{response.data['id']}")
    except tweepy.errors.TweepyException as e:
        print(f"❌ Error posting to X: {e}")
        # This can happen for many reasons, e.g., duplicate tweet, text too long, etc.
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

def main():
    """
    Main function to run the script logic.
    Usage:
    - python main.py : Automatically finds and posts the most recent file.
    - python main.py <filename.txt> : Posts the content of the specified file.
    """
    print("--- Starting Automated X Poster ---")
    
    file_to_post = None

    # Check if a specific filename was provided as a command-line argument
    if len(sys.argv) > 1:
        # Manual mode: Use the provided filename
        file_to_post = sys.argv[1]
        print(f"📌 Manual mode: Using specified file: {file_to_post}")
        if not os.path.exists(file_to_post):
            print(f"❌ Error: The specified file '{file_to_post}' was not found.")
            return
    else:
        # Automatic mode: Find the most recent file
        print("🔄 Automatic mode: Finding the most recent file...")
        file_to_post = find_most_recent_file(TARGET_DIRECTORY)

    if not file_to_post:
        print("🛑 No file to process. Exiting.")
        return

    client = get_api_client()
    if not client:
        return # Stop if authentication fails

    content = read_file_content(file_to_post)
    if not content:
        return # Stop if file is empty or unreadable

    post_to_x(client, content)
    
    print("--- Script finished ---")


if __name__ == "__main__":
    main()
