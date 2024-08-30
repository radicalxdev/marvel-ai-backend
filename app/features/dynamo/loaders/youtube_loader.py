from langchain_community.document_loaders import YoutubeLoader
from app.api.error_utilities import VideoTranscriptError

class YoutubeTranscriptLoader:
    def __init__(self, url: str):
        self.url = url

    def load(self) -> list:
        try:
            loader = YoutubeLoader.from_youtube_url(self.url, add_video_info=True)
            docs = loader.load()
        except Exception as e:
            raise VideoTranscriptError(f"No video found or failed to load transcript: {e}")
        return docs
