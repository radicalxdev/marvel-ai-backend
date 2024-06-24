__author__ = '1. Sanith Kumar Pallerla'
__email__ = '1. pallerlasanithkumar@gmail.com'
__status__ = 'Development'

from typing import List

from langchain_community.document_loaders import YoutubeLoader
from langchain_core.documents import Document
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

from services.tool_registry import ToolFile


class CustomYoutubeLoader:

    def __init__(self, verbose=None):
        self.verbose = verbose

    def transcript_check(self, video_id):
        '''This Function is extract data from youtube url'''
        # return None or YouTubeTranscriptApi.get_transcript(video_id=self.video_id, languages=['en',
        #                                                                                       'en-GB',
        #                                                                                       'en-US'])
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id=video_id,
                                                             languages=['en', 'en-GB', 'en-US', 'en-AU', 'en-BZ',
                                                                        'en-CA', 'en-IE', 'en-JM', 'en-NZ', 'en-ZA',
                                                                        'en-TT', 'en-GB'])
        except:
            return False
        return transcript

    def extract_audio_data(self):
        '''This function is to extract data'''
        pass

    def audio_to_transcript(self):
        '''This function is to convert audio to text'''
        pass

    def load(self, files: List[ToolFile]) -> List[Document]:
        '''
        Step 1 : Check whether Transcript is available or not
            Step 1.1 : Get the transcript based on time stamps
        Step 2 : If Transcript isn't available - UNDER DEVELOPMENT
            Step 2.1 : Extract audio based on time stamps
            Step 2.2 : Convert audio into text
        Step 3 : Load data into lang chain suitable format
        '''

        url = files.url
        start_timestamp = files.start_timestamp
        end_timestamp = files.end_timestamp

        video_id = YoutubeLoader.extract_video_id(url)

        # Un Comment below variables if needed in meta data
        # video_obj = YouTube(url)
        # videolength = video_obj.length
        # video_title = video_obj.title
        # video_author = video_obj.author

        data = ''
        documents = []

        transcript_data = self.transcript_check(video_id)
        if transcript_data:
            if files.start_timestamp == 0.0 and files.end_timestamp == None:
                '''For start to end'''
                for each_data_point in transcript_data:
                    data = data + '\n' + each_data_point['text']
                metadata = {
                    'source': video_id,
                    'start time': start_timestamp,
                    'end time': each_data_point['start'] + each_data_point['duration']
                }
            elif start_timestamp > 0.0 and end_timestamp == None:
                '''From Specific time point to end'''
                for each_data_point in transcript_data:
                    if each_data_point['start'] > start_timestamp:
                        data = data + '\n' + each_data_point['text']
                metadata = {
                    'source': video_id,
                    'start time': start_timestamp,
                    'end time': each_data_point['start'] + each_data_point['duration']
                }
                # return documents.append(
                #     Document(
                #         page_content=data,
                #         metadata=metadata
                #     )
                # )
                # pass
            elif start_timestamp == 0.0 and end_timestamp != None:
                '''From start to specific time point'''
                for each_data_point in transcript_data:
                    if each_data_point['start'] + each_data_point['duration'] < end_timestamp:
                        data = data + '\n' + each_data_point['text']
                metadata = {
                    'source': video_id,
                    'start time': start_timestamp,
                    'end time': end_timestamp
                }
                # return documents.append(
                #     Document(
                #         page_content=data,
                #         metadata=metadata
                #     )
                # )
                # pass
            elif start_timestamp != 0.0 and end_timestamp != None:
                '''From Specific Time point to specific time point'''
                for each_data_point in transcript_data:
                    if each_data_point['start'] > start_timestamp and each_data_point['start'] + each_data_point[
                        'duration'] < end_timestamp:
                        data = data + '\n' + each_data_point['text']
                metadata = {
                    'source': video_id,
                    'start time': start_timestamp,
                    'end time': end_timestamp
                }

                # return documents.append(
                #     Document(
                #         page_content=data,
                #         metadata=metadata
                #     )
                # )
                # pass
            else:
                raise ValueError(
                    f"Unexpected Value Types: "
                    f"start timestamp -> int or float or None, end timestamp -> int or float or None; "
                    f"but got: "
                    f"start timestamp -> {start_timestamp}, end timestamp -> {end_timestamp}"
                )
            document_data = Document(
                page_content=data,
                metadata=metadata
            )
            documents.append(
                document_data
            )

            return documents
        else:
            raise ValueError(
                f"Transcript Not Found"
            )

            # The below feature under development, not ready to be used

            from langchain.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader
            from langchain_community.document_loaders.generic import GenericLoader
            from langchain_community.document_loaders.parsers.audio import FasterWhisperParser
            import os

            loader = GenericLoader(YoutubeAudioLoader([url], os.getcwd()), FasterWhisperParser())
            return loader.load()
            '''
            Step 1 : Extract audio from youtube video
            Step 2 : Convert Audio to Text
            '''

        pass


class CommunityYoutubeLoader:
    '''
    This Class uses built-in Lang Chain fucntions to load data from youtube URL
    '''

    def __init__(self, url: str, start_timestamp=0.0, end_timestamp=None):
        self.url = url
        self.start = start_timestamp
        self.end = end_timestamp

    def load(self) -> List[Document]:

        documents = []

        if self.start == 0.0 and self.end == None:
            loader = YoutubeLoader.from_youtube_url(
                # "https://www.youtube.com/watch?v=QsYGlZkevEg",
                self.url,
                add_video_info=True,
                language=["en", "id"],
                translation="en",
            )
            return documents.append(loader.alazy_load())
        else:
            pass
