from wsgiref import headers

import eyed3
from utils import clStr, decade_from_date, write_genre, get_year_mb
import logging
import requests
from bs4 import BeautifulSoup

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
    if ' - ' in str(mp3_file): 
        tmpArr = str(mp3_file).split(' - ')
        mp3info['artist'] = clStr(tmpArr[0])
        mp3info['title'] = clStr(tmpArr[1])
        logging.debug('return parsed tag %s %s', str(mp3_file), mp3info['artist'])
        return mp3info
    return None


def get_artist_genre(artist, curated_dict, api_dict, mb_dict, allow_genre):
    artist_name = artist['artist'].lower()
    logging.debug("   Getting genre for artist: %s", artist_name)
    if artist_name in curated_dict:
        logging.debug("   found curated genre for artist: %s", artist_name)
        write_genre(artist_name, curated_dict[artist_name], "curated")
        return curated_dict[artist_name], get_year_mb(artist_name, mb_dict)
    elif artist_name in api_dict:
        genres = api_dict[artist_name]
        logging.debug("   found API genre for artist: %s, genre: %s", artist_name, genres)
        for genre in genres:
             logging.debug("   Checking genre: %s", genre)
             if genre in allow_genre:
                logging.debug("   genre allowed: %s", allow_genre[genre])
                write_genre(artist_name, allow_genre[genre], "api")
                return allow_genre[genre], get_year_mb(artist_name, mb_dict)
        logging.info("   No allowed genre found for artist: %s, API genres: %s", artist_name, genres)
    elif artist_name in mb_dict:
        genres = mb_dict[artist_name]['genres']
        logging.debug("   found MB genre for artist: %s, genre: %s", artist_name, genres)
        if genres in allow_genre:
            logging.debug("   genre allowed: %s", allow_genre[genres])
            write_genre(artist_name, allow_genre[genres], "mb")
            return allow_genre[genres], get_year_mb(artist_name, mb_dict)
        logging.info("   No allowed genre found for artist: %s, MB genres: %s", artist_name, genres)
    elif 'genre' in artist:
        if artist['genre'] in allow_genre:
            logging.debug("   genre from tag allowed: %s", allow_genre[artist['genre']])
            write_genre(artist_name, allow_genre[artist['genre']], "tag")
            return allow_genre[artist['genre']], get_year_mb(artist_name, mb_dict)
        logging.info("   No genre found for artist: %s", artist_name)    
    else:
        write_genre(artist_name, "unknown", "unknown")
        return None, None
    write_genre(artist_name, "unknown", "unknown")
    return None, None

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

    def find_genre(self, curated_dict, api_dict, mb_dict, allow_genre):
        if hasattr(self, 'artist'):

            self.genre_calc, self.decade_artist = get_artist_genre({'artist': self.artist}, curated_dict, api_dict, mb_dict, allow_genre)
        else:
            self.genre_calc = ''
            self.decade_artist = ''

    def get_popularity(self):
        if hasattr(self, 'artist') and hasattr(self, 'title'):
            print(f"Getting popularity for {self.artist} - {self.title}")
            search = self.artist + " " + self.title
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
            html = requests.get('https://www.youtube.com/results?search_query='+search, headers=headers).text
            print(html)
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.find_all('a'):
                if '/watch?v=' in link.get('href'):
                    print(link.get('href'))
                    # May change when Youtube Website may get updated in the future.
                    video_link = link.get('href')



    def __str__(self):
        if hasattr(self, 'genre_calc') and hasattr(self, 'artist') and hasattr(self, 'decade_artist'):
            return f"{self.artist} {self.title} ({self.genre_calc}, {self.decade_artist})"
        elif hasattr(self, 'artist') and hasattr(self, 'title'):
            return f"{self.artist} {self.title} ({self.genre}, {self.year})"
        else:
            return f"{self.name} (metadata not found)"
    