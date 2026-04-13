import logging
import pprint as pp
import argparse, json
from genre import load_ressource, get_artist_genre, load_ressource_json
from file import get_mp3_info, get_all_mp3_files, write_info, get_year
from utils import clStr


curated_file = 'ressource/groupe_curated.tsv'
api_file = 'ressource/art_grp.tsv'
allow_file = 'ressource/allowed_genre.tsv'
artist_file_mb = 'ressource/artistes.json'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Command line arguments: -p/--path for target path, -d/--db for database file
parser = argparse.ArgumentParser(description='Build music DB from mp3 files')
parser.add_argument('-p', '--path', required=True, help='Path to search for mp3 files')
args = parser.parse_args()



if (__name__ == "__main__"):
    logging.info("Start Music Curator NG")
    artiste_curated = load_ressource(curated_file)
    #pp.pprint(artiste_curated)
    artiste_api = load_ressource(api_file)
    #pp.pprint(artiste_api)
    allow_genre = load_ressource(allow_file)
    #pp.pprint(allow_genre)
    artiste_mb = load_ressource_json(artist_file_mb)
    #pp.pprint(artiste_mb)
    if args.path:
        for mp3_file in get_all_mp3_files(args.path):
            logging.debug("  Processing file: %s", mp3_file)
            mp3_info = get_mp3_info(mp3_file)
            if mp3_info and 'artist' in mp3_info:
                mp3_info['genre_calc'], mp3_info['decade_artist'] = get_artist_genre(mp3_info, artiste_curated, artiste_api, artiste_mb, allow_genre)
                print(json.dumps(mp3_info))
                write_info(mp3_info)
            else:
                logging.warning("No artist info found for file: %s", mp3_file)

    else:
        logging.warning("No path nor database provided, skipping file processing")