import logging
import pathlib
import sqlite3
import pprint as pp
import argparse
import re


curated_file = 'ressource/groupe_curated.tsv'
api_file = 'ressource/art_grp.tsv'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Command line arguments: -p/--path for target path, -d/--db for database file
parser = argparse.ArgumentParser(description='Build music DB from mp3 files')
parser.add_argument('-p', '--path', required=True, help='Path to search for mp3 files')
args = parser.parse_args()


def load_ressource(file_path):
    resource_dict = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('\t')
                if len(parts) == 2:
                    artist_name = parts[0].strip().lower()
                    genre = parts[1].strip().lower()
                    resource_dict[artist_name] = genre
                if len(parts) >= 3:
                    genre1 = parts[0].strip().lower()
                    genre2 = parts[1].strip().lower()
                    genre3 = parts[2].strip().lower()
                    genre4 = parts[3].strip().lower()
                    artist_name = parts[4].strip().lower()
                    count = parts[5].strip().lower()
                    resource_dict[artist_name] = (genre1, genre2, genre3, genre4, count)
    logging.info("Curated artists loaded: %s", len(resource_dict))
    return resource_dict

def get_artist_genre(artist_name, curated_dict, api_dict):
    artist_name = artist_name.lower()
    if artist_name in curated_dict:
        return curated_dict[artist_name]
    elif artist_name in api_dict:
        return api_dict[artist_name]
    else:
        return None

def get_all_mp3_files(path):
    logging.info("Scanning path for mp3 files: %s", path)
    Todo = []
    for path in sorted(pathlib.Path(path).rglob('*mp3')):
        if path.is_file() :
            Todo.append(path)
    return Todo

def clStr(MyStr):
    if MyStr == '' or MyStr is None:
        return ''
    #retStr = ''.join(filter(str.isalnum, MyStr))
    retStr = re.sub(r'[^a-zA-Z0-9éèàç&êöë \-]', ' ', MyStr)
    retStr = retStr.title()
    return str(retStr)

def get_mp3_info(mp3_file):
    mp3info= {}
    try:
        audio = eyed3.load(mp3_file)
        if audio:
            if audio.tag:
                mp3info['artist'] = clStr(audio.tag.artist)
                mp3info['title'] = clStr(audio.tag.title)
                mp3info['album'] = clStr(audio.tag.album)
                if audio.tag.genre:
                    mp3info['genre']  = clStr(audio.tag.genre.name)
            if len(mp3info['artist']) > 0:
                logging.debug('return audio tag %s %s', str(fullfile), mp3info['artist'])
                return mp3info
    except Exception as e:
        logging.error("Error reading mp3 file %s : %s", str(fullfile), str(e))
    if ' - ' in str(fullfile.name): 
        tmpArr = str(fullfile.name).split(' - ')
        mp3info['artist'] = clStr(tmpArr[0])
        mp3info['title'] = clStr(tmpArr[1])
        logging.debug('return parsed tag %s %s', str(fullfile), mp3info['artist'])
        return mp3info
    return None

if (__name__ == "__main__"):
    logging.info("Start Music Curator NG")
    artiste_curated = load_ressource(curated_file)
    #pp.pprint(artiste_curated)
    artiste_api = load_ressource(api_file)
    #pp.pprint(artiste_api)
    if args.path:
        logging.warning("Path provided: %s", args.path)
        get_all_mp3_files(args.path)
        for mp3_file in get_all_mp3_files(args.path):
            logging.info("Processing file: %s", mp3_file)
            get_mp3_info(mp3_file)

    else:
        logging.warning("No path nor database provided, skipping file processing")