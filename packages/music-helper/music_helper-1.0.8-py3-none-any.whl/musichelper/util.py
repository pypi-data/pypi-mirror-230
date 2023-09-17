import re
import hashlib
import unicodedata
import string
from os import path
import pathlib
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import requests



def clean_query(query):
    # A pure copy-paste of regex patterns from DeezloaderRemix
    # I dont know regex

    query = re.sub(r"/ feat[\.]? /g", " ", query)
    query = re.sub(r"/ ft[\.]? /g", " ", query)
    query = re.sub(r"/\(feat[\.]? /g", " ", query)
    query = re.sub(r"/\(ft[\.]? /g", " ", query)
    query = re.sub(r"/\&/g", "", query)
    query = re.sub(r"/–/g", "-", query)
    query = re.sub(r"/–/g", "-", query)

    return query


def create_folders(directory):
    directory = path.normpath(directory)

    p = pathlib.Path(directory)
    p.mkdir(parents=True, exist_ok=True)


def clean_filename(filename):
    # https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8
    whitelist = "-_.() %s%s" % (string.ascii_letters,
                                string.digits) + "',&#$%@`~!^&+=[]{}"
    char_limit = 255
    replace = ''

    # replace spaces
    for r in replace:
        filename = filename.replace(r, '_')

    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize(
        'NFKD', filename).encode('ASCII', 'ignore').decode()

    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename) > char_limit:
        print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit]


def get_text_md5(text, encoding="UTF-8"):
    return hashlib.md5(str(text).encode(encoding)).hexdigest()


def get_blowfish_key(track_id):
    secret = 'g4el58wc0zvf9na1'

    m = hashlib.md5()
    m.update(bytes([ord(x) for x in track_id]))
    id_md5 = m.hexdigest()

    blowfish_key = bytes(([(ord(id_md5[i]) ^ ord(id_md5[i+16]) ^ ord(secret[i]))
                           for i in range(16)]))

    return blowfish_key

async def apply_tags(file_path:str, data:dict):
    audio = MP3(file_path, ID3=EasyID3)
    audio.delete()
    EasyID3.RegisterTextKey("label", "TPUB")

    cover = data.get('_albumart', "no deezer")

    if cover != "no deezer":
        del data["_albumart"]
    else: 
        cover = data.get('cover', None)
        del data["cover"]
    

    for key in ["title", "artist", "album"]:
        val = data.get(key)
        if val:
            audio[key] = str(val)
    

    audio.save()
    
    if isinstance(cover, str):
        response = requests.get(cover)
        if response.status_code == 200:
            image_data = response.content
            mime_type = response.headers.get("Content-Type")
            cover = {
                "image": image_data,
                "mime_type": mime_type
            }
        else:
            cover = {
                "image": b'',
                "mime_type": 'image/jpeg'
            }



    if cover:
        cover_handle = ID3(file_path)
        cover_handle["APIC"] = APIC(
            type=3,
            mime=cover["mime_type"],
            data=cover["image"]
        )
        cover_handle.save(file_path)

    
    
