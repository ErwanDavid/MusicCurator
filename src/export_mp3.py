import sqlite3
import logging
import argparse





logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Command line arguments: -p/--path for target path, -d/--db for database file
parser = argparse.ArgumentParser(description='Move song to right folder')
parser.add_argument('-d', '--dbfile', required=True, help='Path to the database file')
parser.add_argument('-p', '--path', required=True, help='Path to the target folder')
parser.add_argument('-m', '--maxPerArtist', type=int, default=15, help='Maximum number of songs per artist')
args = parser.parse_args()



def get_all_artists_from_db(dbfile):
    conn = sqlite3.connect(dbfile)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT artist FROM music")
    artists = [row[0] for row in cursor.fetchall()]
    conn.close()
    return artists


all_Artists = get_all_artists_from_db(args.dbfile)
for artist in all_Artists:
    logging.info(f"Processing artist: {artist}")
    conn = sqlite3.connect(args.dbfile)
    cursor = conn.cursor()
    cursor.execute("SELECT path, artist, title, nb_views, genre_calc FROM music WHERE artist = ? ORDER BY nb_views DESC", (artist,))
    songs = cursor.fetchall()
    conn.close()
    for i, song in enumerate(songs):
        if i < args.maxPerArtist:
            logging.info(f"Keeping song: {song[1]} - {song[2]} (Popularity: {song[3]})")
        else:
            logging.info(f"Excluding song: {song[1]} - {song[2]} (Popularity: {song[3]})")