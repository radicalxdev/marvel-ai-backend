import re

def extract_folder_id(url):
    # Regular expression pattern to match the folder ID in the URL
    pattern = r"https://drive\.google\.com/drive/u/\d+/folders/([a-zA-Z0-9-_]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None