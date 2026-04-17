import re
import pathlib
import eyed3
from utils import clStr, decade_from_date, get_year_mb
import logging
import requests
from bs4 import BeautifulSoup

def compute_score(nb_views):
    if nb_views   > 500000000:
        return 'A'
    elif nb_views > 80000000:
        return 'B'
    elif nb_views > 10000000:
        return 'C'
    elif nb_views > 2000000:
        return 'D'
    elif nb_views > 100000:
        return 'E'
    else:
        return 'F'

def get_mp3_info(mp3_file):
    mp3info= {}
    try:
        audio = eyed3.load(mp3_file)
        if audio:
            if audio.tag:
                mp3info['artist'] = clStr(audio.tag.artist)
                mp3info['title']  = clStr(audio.tag.title)
                mp3info['album']  = clStr(audio.tag.album)
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
    short_name = pathlib.Path(mp3_file).name
    if ' - ' in short_name: 
        tmpArr = short_name.split(' - ')
        mp3info['artist'] = clStr(tmpArr[0])
        mp3info['title'] = clStr(tmpArr[1]).replace('mp3', '')
        logging.debug('return parsed tag %s %s', str(mp3_file), mp3info['artist'])
        return mp3info
    return None


def get_artist_genre(artist, curated_dict, api_dict, mb_dict, allow_genre):
    artist_name = artist['artist'].lower()
    logging.debug("   Getting genre for artist: %s", artist_name)
    if artist_name in curated_dict:
        logging.debug("   found curated genre for artist: %s", artist_name)
        return curated_dict[artist_name], get_year_mb(artist_name, mb_dict), "curated"
    elif artist_name in api_dict:
        genres = api_dict[artist_name]
        logging.debug("   found API genre for artist: %s, genre: %s", artist_name, genres)
        for genre in genres:
             logging.debug("   Checking genre: %s", genre)
             if genre in allow_genre:
                logging.debug("   genre allowed: %s", allow_genre[genre])
                return allow_genre[genre], get_year_mb(artist_name, mb_dict), "api"
        logging.info("   No allowed genre found for artist: %s, API genres: %s", artist_name, genres)
    elif artist_name in mb_dict:
        genres = mb_dict[artist_name]['genres']
        logging.debug("   found MB genre for artist: %s, genre: %s", artist_name, genres)
        if genres in allow_genre:
            logging.debug("   genre allowed: %s", allow_genre[genres])
            return allow_genre[genres], get_year_mb(artist_name, mb_dict), "mb"
        logging.info("   No allowed genre found for artist: %s, MB genres: %s", artist_name, genres)
    elif 'genre' in artist:
        if artist['genre'] in allow_genre:
            logging.debug("   genre from tag allowed: %s", allow_genre[artist['genre']])
            return allow_genre[artist['genre']], get_year_mb(artist_name, mb_dict), "tag"
        logging.info("   No genre found for artist: %s", artist_name)    
    else:
        return None, None, None
    return None, None, None

class musicfile:
    def __init__(self, fullname):
        self.name = fullname

    def get_metadata(self):
        mp3_info = get_mp3_info(self.name)
        if mp3_info:
            self.artist = mp3_info.get('artist', '')
            self.title = mp3_info.get('title', '')
            self.album = mp3_info.get('album', '')
            self.genre = mp3_info.get('genre', '')
            self.year = mp3_info.get('year', '')
            self.decade = mp3_info.get('decade', '')

    def get_genre(self, curated_dict, api_dict, mb_dict, allow_genre):
        if hasattr(self, 'artist'):

            self.genre_calc, self.decade_artist, self.genre_src = get_artist_genre({'artist': self.artist}, curated_dict, api_dict, mb_dict, allow_genre)
        else:
            self.genre_calc = ''
            self.decade_artist = ''
            self.genre_src = ''

    def get_popularity(self):
        if hasattr(self, 'artist') and hasattr(self, 'title'):
            search = self.artist + " " + self.title
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
            try:
                html = requests.get('https://www.youtube.fr/results?search_query='+search, headers=headers).text
                soup = BeautifulSoup(html, 'html.parser')
                nb_views = re.search(r'(\d[\d\s]*\d)\s+v', soup.prettify()).group(1)
                nb_views = re.sub(r"\D", "", nb_views)
                self.nb_views = int(nb_views)
                logging.debug(f"Popularity for {self.artist} {self.title}: {self.nb_views}")
                self.popularity = compute_score(self.nb_views)
            except Exception as e:
                logging.error(f"Error fetching popularity for {self.artist} {self.title}: {e}")
                self.popularity = 'F'



    def __str__(self):
        if hasattr(self, 'decade') and hasattr(self, 'popularity'):
            str = f"{self.genre_calc}//{self.artist} - {self.title}_{self.decade}_{self.popularity}"
        elif hasattr(self, 'decade_artist') and hasattr(self, 'popularity'):
            str = f"{self.genre_calc}//{self.artist} - {self.title}_{self.decade_artist}_{self.popularity}"
        elif hasattr(self, 'genre_calc') and hasattr(self, 'popularity'):
            str = f"{self.genre_calc}//{self.artist} - {self.title}_{self.popularity}"
        elif hasattr(self, 'genre_calc'):
            str = f"{self.genre_calc}//{self.artist}//{self.title}"
        else:
            str =  f"{self.name} (metadata not found)"
        logging.info(f"RES ==> {str}")
        return str
    