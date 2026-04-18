import logging, argparse
import os
import musicfile
import utils
import db
import shutil



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

curated_file = 'ressource/groupe_curated.tsv'
api_file = 'ressource/art_grp.tsv'
allow_file = 'ressource/allowed_genre.tsv'
artist_file_mb = 'ressource/artistes.json'

# Command line arguments: -p/--path for target path, -d/--db for database file
parser = argparse.ArgumentParser(description='Build music DB from mp3 files')
parser.add_argument('-p', '--path', required=True, help='Path to search for mp3 files')
parser.add_argument('-d', '--dbfile', required=True, help='Path to the database file')
args = parser.parse_args()

def copy_file(mp3_file, mp3_info):
    #wrtite to file log
    if 'artist' in mp3_info:
        dst_dir = f"{args.dst}/{mp3_info['genre_calc']}/{mp3_info['artist']}"
    else:
        dst_dir = f"{args.dst}/{mp3_info['genre_calc']}/unknown_artist"
    os.makedirs(dst_dir, exist_ok=True)
    if 'title' in mp3_info:
        dst = f"{dst_dir}/{mp3_info['title']}_{mp3_info.get('decade', '')}_{mp3_info.get('popularity', '')}.mp3"
        write_str= f"copy {mp3_file} {dst}\n"
        shutil.copyfile(mp3_file, dst)
        open('db/result_net.txt', 'a').write(write_str)


if (__name__ == "__main__"):
    logging.info("Start Music Curator NG")
    db.init_db(args.dbfile)
    artiste_curated = utils.load_ressource(curated_file)
    #pp.pprint(artiste_curated)
    artiste_api = utils.load_ressource(api_file)
    #pp.pprint(artiste_api)
    allow_genre = utils.load_ressource(allow_file)
    #pp.pprint(allow_genre)
    artiste_mb = utils.load_ressource_json(artist_file_mb)
    #pp.pprint(artiste_mb)
    cpt = 0
    if args.path:
        file_list = utils.get_all_mp3_files(args.path)
        for mp3_file in file_list:
            cpt += 1
            logging.info(f" Processing file: {mp3_file} ({cpt}/{len(file_list)})")
            cur_file = musicfile.musicfile(mp3_file)
            cur_file.get_metadata()
            cur_file.get_genre(artiste_curated, artiste_api, artiste_mb, allow_genre)
            cur_file.get_popularity()
            #copy_file(mp3_file,cur_file.__dict__)
            if 'md5' in cur_file.__dict__:
                 db.insert_file_info_to_database(mp3_file, cur_file.__dict__, args.dbfile)