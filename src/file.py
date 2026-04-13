import pathlib
import eyed3
from utils import clStr, decade_from_date
import logging
import discogs_client

def get_mp3_info(mp3_file):
    mp3info= {}
    try:
        audio = eyed3.load(mp3_file)
        if audio:
            if audio.tag:
                mp3info['artist'] = clStr(audio.tag.artist)
                mp3info['title'] = clStr(audio.tag.title)
                mp3info['album'] = clStr(audio.tag.album)
                year = audio.tag.original_release_date or audio.tag.release_date or audio.tag.recording_date
                if year:
                    mp3info['year'] = clStr(str(year))
                    mp3info['decade'] = decade_from_date(year)
                if audio.tag.genre:
                    mp3info['genre']  = clStr(audio.tag.genre.name)
            if len(mp3info['artist']) > 0:
                logging.debug('return audio tag %s %s', str(mp3_file), mp3info['artist'])
                return mp3info
    except Exception as e:
        logging.error("Error reading mp3 file %s : %s", str(mp3_file), str(e))
    if ' - ' in str(mp3_file.name): 
        tmpArr = str(mp3_file.name).split(' - ')
        mp3info['artist'] = clStr(tmpArr[0])
        mp3info['title'] = clStr(tmpArr[1])
        logging.debug('return parsed tag %s %s', str(mp3_file), mp3info['artist'])
        return mp3info
    return None

def write_info(mp3_info):
    #wrtite to file log
    write_str= f"{mp3_info['genre_calc']}\t{mp3_info['artist']}\t{mp3_info.get('decade', '')}\t{mp3_info['title']}.mp3\n"
    open('db/result2.txt', 'a').write(write_str)
   
def get_all_mp3_files(path):
    logging.info("   Scanning path for mp3 files: %s", path)
    Todo = []
    for path in pathlib.Path(path).rglob('*.mp3'):
        if path.is_file() :
            Todo.append(path)
    logging.info("   Total mp3 files found: %s", len(Todo))
    return Todo

def get_year(artist, title):
    #try to get year from discogs

    d = discogs_client.Client('MusicCurator/1.0')
    try:
        results = d.search(artist, type='artist')
        if results:
            artist_id = results[0].id
            artist_data = d.artist(artist_id)
            for release in artist_data.releases:
                if release.title.lower() == title.lower():
                    return release.year
    except Exception as e:
        logging.error("Error fetching year from Discogs for %s - %s: %s", artist, title, str(e))
    return None