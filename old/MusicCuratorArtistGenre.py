import eyed3
import logging

import sys, re
import pathlib
import sqlite3


def createTable(cursor_obj):
    logging.info("CREATE TABLE")
    cursor_obj.execute("DROP TABLE IF EXISTS GENRE")
    table = """ CREATE TABLE GENRE (
                artist	VARCHAR(255) NOT NULL,
                genre	VARCHAR(255) NOT NULL,
                nbr     INTEGER default 1,
                CONSTRAINT pk_art PRIMARY KEY(artist,genre)
            ); """
    cursor_obj.execute(table)

def AddEntry(cursor_obj,artist, genre):
    conn.execute('''INSERT INTO GENRE (artist, genre)
                    VALUES (?,?)
                    ON CONFLICT(artist, genre) DO UPDATE SET nbr = nbr + 1''',    (artist, genre))
    conn.commit()


def get_all_path(directory):
    logging.info("    _get_all_path from %s", directory)
    Todo = []
    for path in sorted(pathlib.Path(directory).rglob('*mp3')):
        if path.is_file() :
            #print("\tAdding on ",str(path))
            Todo.append(path)
    return Todo

def clStr(MyStr):
    if MyStr == '' or MyStr is None:
        retStr = "Unknown"
        return str(retStr)
    #retStr = ''.join(filter(str.isalnum, MyStr))
    retStr = re.sub(r'[^a-zA-Z0-9éèàç&êöë \-]', ' ', MyStr)
    retStr = retStr.title()
    if retStr == '':
        retStr = "Unknown"
    return str(retStr)

def GetfromMp3(fullfile):
    audio = eyed3.load(fullfile)
    mp3info= {}
    if audio:
        if audio.tag:
            mp3info['artist'] = clStr(audio.tag.artist)
            if audio.tag.genre:
                mp3info['genre']  = clStr(audio.tag.genre.name)
                return mp3info

def generateArtistGenre(QueryCurs, big_list):
    for song in big_list:
        insertArtist = GetfromMp3(song)
        if insertArtist:
            AddEntry(QueryCurs, insertArtist['artist'], insertArtist['genre'])


conn = sqlite3.connect("./artist.db")
QueryCurs = conn.cursor()
#if needCreate() :
createTable(QueryCurs)

global_Todo =  get_all_path(sys.argv[1])
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("BIG LIST : %s", len(global_Todo))
generateArtistGenre(QueryCurs, global_Todo)

# curl "https://ws.audioscrobbler.com/2.0/?method=artist.gettopTags&artist=indochine&user=RJ&api_key=b25b959554ed76058ac220b7b2e0a026&format=json"

