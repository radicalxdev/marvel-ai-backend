from langchain_community.document_loaders.base import BaseLoader
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.schema import Document

def fetch_transcript(video_id):
    # Fetch transcript using YouTubeTranscriptApi
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return transcript

def create_text_content(transcript):
    # Create plain text content from the transcript
    text_content = "Transcript\n\n"
    for entry in transcript:
        start_time = entry['start']
        minutes = int(start_time // 60)
        seconds = int(start_time % 60)
        timestamp = f"{minutes}:{seconds:02d}"
        text_content += f"{timestamp}\n{entry['text']}\n"
    return text_content

def create_document(text_content, url):
    # Create a Document object with page content and metadata
    doc = Document(page_content=text_content, metadata={"source": url})
    return doc

# Example usage
video_id = "z71utK9Gz00"  # Replace with your YouTube video ID
url = f"https://www.youtube.com/watch?v=z71utK9Gz00"

transcript = fetch_transcript(video_id)
text_content = create_text_content(transcript)
document = create_document(text_content, url)

# Output the document for verification
print(document.page_content)
