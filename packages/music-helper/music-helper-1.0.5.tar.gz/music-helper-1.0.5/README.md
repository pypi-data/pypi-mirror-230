# music-helper | v`1.0.1`


# Installation
`pip install music-helper`

# Usage

```python
from musichelper.MusicHelper import MusicHelper
import asyncio

SoundCloud_DATA = (
    "CLIENT_ID",
    "AUTH_TOKEN"
)
DEEZER_ARL = "change this"
YTM_OAUTH_PATH = "./ytm_oauth.json"

async def main():
    music_api = MusicHelper(deezer_arl = DEEZER_ARL,
                         ytm_oauth = YTM_OAUTH_PATH 
                         sc_data = SoundCloud_DATA,
                         logger = logger)


    # Deezer (Search & Download)
    ## Other methods can be found on the WIKI
    data = await music_api.deezer.search_tracks('post malone rockstar', limit=1)
    deezer_track = await music_api.deezer.get_track(data[0]['id'])
    download_data = await music_api.deezer.download_track(deezer_track['info'],'./', with_lyrics=False, with_metadata=True)
    print(download_data) # {'track': '.\\Post Malone - rockstar (feat. 21 Savage).mp3', 'lyric': None}


    # SoundCloud (Search & Download)
    search_data = await music_api.soundcloud.search('xxxtentacion ghetto christmas carol',limit=1)
    # type(search_data) -> Generator
    
    for track in search_data:
        download_data = await music_api.soundcloud.download_track(track.id, './temp/')
        print(download_data) # "./temp/A GHETTO CHRISTMAS CAROL Prod. RONNY J - XXXTENTACION.mp3"


    # YouTube Music (Search & Download)
    search_data = await music_api.ytm.search('masn - dont talk', filter='songs', limit=1)
    track_tags = {
        'videoId': search_data[0]['videoId'],
        "artist": ', '.join(artist['name'] for artist in search_data[0]['artists']),
        "title":  search_data[0]['title'],
        "album":  search_data[0]['album']['name'] if 'album' in  search_data[0] else " ",
        "cover":  search_data[0]['thumbnails'][-1]['url']
    }

    downlaod_data = await music_api.ytm.download_track(video_id = track_tags['videoId'], 
                download_path = './temp/', track_tags =track_tags)
    print(downlaod_data) # "./temp/MASN - Don't Talk.mp3"

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


```
