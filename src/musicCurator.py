import logging, argparse
import musicfile
import utils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

curated_file = 'ressource/groupe_curated.tsv'
api_file = 'ressource/art_grp.tsv'
allow_file = 'ressource/allowed_genre.tsv'
artist_file_mb = 'ressource/artistes.json'

# Command line arguments: -p/--path for target path, -d/--db for database file
parser = argparse.ArgumentParser(description='Build music DB from mp3 files')
parser.add_argument('-p', '--path', required=True, help='Path to search for mp3 files')
args = parser.parse_args()



if (__name__ == "__main__"):
    logging.info("Start Music Curator NG")
    artiste_curated = utils.load_ressource(curated_file)
    #pp.pprint(artiste_curated)
    artiste_api = utils.load_ressource(api_file)
    #pp.pprint(artiste_api)
    allow_genre = utils.load_ressource(allow_file)
    #pp.pprint(allow_genre)
    artiste_mb = utils.load_ressource_json(artist_file_mb)
    #pp.pprint(artiste_mb)
    if args.path:
        for mp3_file in utils.get_all_mp3_files(args.path):
            logging.debug("  Processing file: %s", mp3_file)
            cur_file = musicfile.musicfile(mp3_file)
            cur_file.get_metadata()
            cur_file.find_genre(artiste_curated, artiste_api, artiste_mb, allow_genre)
            cur_file.get_popularity()
            print(cur_file)