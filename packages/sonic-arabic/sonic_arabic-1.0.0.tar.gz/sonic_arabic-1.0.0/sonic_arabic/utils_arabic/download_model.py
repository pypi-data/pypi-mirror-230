import os
import gdown


def download_file_from_google_drive(url, dest_path):
    try:
        gdown.download(url, dest_path, quiet=False)
    except Exception as e:
        print(f"An error occurred: {e}")


def ensure_file_downloaded(file_path, google_drive_url):
    if not os.path.exists(file_path):
        print(f"{file_path} not found, downloading...")
        download_file_from_google_drive(google_drive_url, file_path)
        if not os.path.exists(file_path):
            print("Failed to download the file.")
        else:
            print(f"{file_path} has been successfully downloaded.")
