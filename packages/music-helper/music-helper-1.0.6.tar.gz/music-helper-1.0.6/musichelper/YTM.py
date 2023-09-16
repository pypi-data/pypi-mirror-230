import ytmusicapi
from pytube import YouTube
import pytube.exceptions as YTExceptions
import os
from logging import Logger
import asyncio
import random
import string

from .util import apply_tags, clean_filename

class YTM:
    def __init__(self, ytm_oauth:str,
                 executor=None,logger:Logger=None) -> None:
        self.ytm_oauth = ytm_oauth
        self.logger = logger
        self.executor = executor

        self.ytm = None
        try:
            if os.path.exists(self.ytm_oauth):
                self.ytm = ytmusicapi.YTMusic(self.ytm_oauth)
            else:
                ytmusicapi.setup_oauth(self.ytm_oauth)
                self.ytm = ytmusicapi.YTMusic(self.ytm_oauth)
        except Exception as ytm_exception:
            if self.logger: logger.error(f'[YTm OAUTH]: {ytm_exception}')

    def generate_name(self, length):
        characters = string.ascii_letters + string.digits 
        return ''.join(random.choice(characters) for _ in range(length))

    async def __search(self, query:str, filter:str, scope:str, 
                       limit:int, ignore_spelling:bool):
        data = self.ytm.search(query = query, filter = filter, scope = scope, 
                               limit = limit, ignore_spelling = ignore_spelling)
        
        return data
    
    async def search(self, query:str, filter:str=None, scope:str=None, 
                       limit:int=20, ignore_spelling:bool=False):
        """
        Search YouTube music
        Returns results within the provided category.

        :param query: Query string, i.e. 'Oasis Wonderwall'
        :param filter: Filter for item types. Allowed values: ``songs``, ``videos``, ``albums``, ``artists``, ``playlists``, ``community_playlists``, ``featured_playlists``, ``uploads``.
          Default: Default search, including all types of items.
        :param scope: Search scope. Allowed values: ``library``, ``uploads``.
            For uploads, no filter can be set! An exception will be thrown if you attempt to do so.
            Default: Search the public YouTube Music catalogue.
        :param limit: Number of search results to return
          Default: 20
        :param ignore_spelling: Whether to ignore YTM spelling suggestions.
          If True, the exact search term will be searched for, and will not be corrected.
          This does not have any effect when the filter is set to ``uploads``.
          Default: False, will use YTM's default behavior of autocorrecting the search.
        :return: List of results depending on filter.
          resultType specifies the type of item (important for default search).
          albums, artists and playlists additionally contain a browseId, corresponding to
          albumId, channelId and playlistId (browseId=``VL``+playlistId)

          Example list for default search with one result per resultType for brevity. Normally
          there are 3 results per resultType and an additional ``thumbnails`` key::

            [
              {
                "category": "Top result",
                "resultType": "video",
                "videoId": "vU05Eksc_iM",
                "title": "Wonderwall",
                "artists": [
                  {
                    "name": "Oasis",
                    "id": "UCmMUZbaYdNH0bEd1PAlAqsA"
                  }
                ],
                "views": "1.4M",
                "videoType": "MUSIC_VIDEO_TYPE_OMV",
                "duration": "4:38",
                "duration_seconds": 278
              },
              {
                "category": "Songs",
                "resultType": "song",
                "videoId": "ZrOKjDZOtkA",
                "title": "Wonderwall",
                "artists": [
                  {
                    "name": "Oasis",
                    "id": "UCmMUZbaYdNH0bEd1PAlAqsA"
                  }
                ],
                "album": {
                  "name": "(What's The Story) Morning Glory? (Remastered)",
                  "id": "MPREb_9nqEki4ZDpp"
                },
                "duration": "4:19",
                "duration_seconds": 259
                "isExplicit": false,
                "feedbackTokens": {
                  "add": null,
                  "remove": null
                }
              },
              {
                "category": "Albums",
                "resultType": "album",
                "browseId": "MPREb_9nqEki4ZDpp",
                "title": "(What's The Story) Morning Glory? (Remastered)",
                "type": "Album",
                "artist": "Oasis",
                "year": "1995",
                "isExplicit": false
              },
              {
                "category": "Community playlists",
                "resultType": "playlist",
                "browseId": "VLPLK1PkWQlWtnNfovRdGWpKffO1Wdi2kvDx",
                "title": "Wonderwall - Oasis",
                "author": "Tate Henderson",
                "itemCount": "174"
              },
              {
                "category": "Videos",
                "resultType": "video",
                "videoId": "bx1Bh8ZvH84",
                "title": "Wonderwall",
                "artists": [
                  {
                    "name": "Oasis",
                    "id": "UCmMUZbaYdNH0bEd1PAlAqsA"
                  }
                ],
                "views": "386M",
                "duration": "4:38",
                "duration_seconds": 278
              },
              {
                "category": "Artists",
                "resultType": "artist",
                "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA",
                "artist": "Oasis",
                "shuffleId": "RDAOkjHYJjL1a3xspEyVkhHAsg",
                "radioId": "RDEMkjHYJjL1a3xspEyVkhHAsg"
              }
            ]


        """
        task = await asyncio.get_event_loop().run_in_executor(self.executor, 
                        lambda: self.__search(query = query, filter = filter, 
                                             scope = scope, limit = limit, 
                                             ignore_spelling = ignore_spelling))
        
        
        task_result = await task
        return task_result


    async def __download_track(self, video_id:str, download_path:str, filename:str=None, is_song:bool=False, track_tags:dict=None):
        try:
            if self.logger: self.logger.info(f'[YTM-DL] [{video_id}]: Start downloading')
            full_tempfile = None
            video = YouTube(f'https://www.youtube.com/watch?v={video_id}')
            audio_stream = video.streams.get_audio_only()
            if is_song and track_tags is None:
                if self.logger: self.logger.info(f'[YTM-DL] [{video_id}]: Search the track tags')
                temp_track_tags = await self.search(query = f"{video.author} - {video.title}", filter = 'songs',limit = 1)
                if temp_track_tags:
                    track = temp_track_tags[0]
                    track_tags = {
                        "artist": ', '.join(artist['name'] for artist in track['artists']),
                        "title":track['title'],
                        "album": track['album']['name'] if 'album' in track else " ",
                        "cover": track['thumbnails'][-1]['url']
                    }
                else:
                    if self.logger: self.logger.info(f'[YTM-DL] [{video_id}]: Tags not found..')

            if not os.path.exists('./temp'):
                os.mkdir('./temp/')


            temp_file_name = f"{self.generate_name(10)}_temp.mp3"
            temp_file_dir = './temp/'
            full_tempfile = temp_file_dir + temp_file_name
            if self.logger: self.logger.info(f'[YTM-DL] [{video_id}]: Downloading.....')
            audio_stream.download(
                temp_file_dir,
                temp_file_name
            )
            if filename:
                finally_filepath = download_path + clean_filename(filename)
            else:
                if track_tags:
                    finally_filepath = download_path + clean_filename(f"{track_tags['artist']} - {track_tags['title']}.mp3")
                else:
                    finally_filepath = download_path + clean_filename(f"{video.author} - {video.title}.mp3")
            
            
            if self.logger: self.logger.info(f'[YTM-DL] [{video_id}]: Fixing audio file...')
            command = f'ffmpeg -i "{full_tempfile}" -vn -acodec libmp3lame -loglevel quiet -q:a 0 "{finally_filepath}"'
            os.system(command)
            os.remove(full_tempfile)

            if track_tags:
                if self.logger: self.logger.info(f'[YTM-DL] [{video_id}]: Setting tags to audio...')
                await apply_tags(finally_filepath, track_tags)

            return finally_filepath


        except YTExceptions.RegexMatchError:
            return None
        except BaseException as err:
            if self.logger: self.logger.error(f'[YTM-DL] [{video_id}] ERROR: {err}')


    async def download_track(self, video_id:str, download_path:str, filename:str=None, is_song:bool=False, track_tags:dict=None):
        """
          Download YouTube video as a track
        
          
          :param video_id: ID VIdeo YouTube
          :param download_path: Download directory
          :param download_path: File name
        """
        
        task = await asyncio.get_event_loop().run_in_executor(self.executor, 
                        lambda: self.__download_track(
                                         video_id = video_id, download_path = download_path, 
                                         filename = filename, is_song = is_song, track_tags = track_tags))
        
        
        task_result = await task
        return task_result
        
        
