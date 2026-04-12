import requests
import eyed3
import logging
import argparse

import re
import pathlib, hashlib
import sqlite3
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'disable_existing_loggers': False,   # keep library loggers available for configuration
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG',
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'requests': {'level': 'WARNING'},
        'urllib3': {'level': 'WARNING'},
        'eyed3': {'level': 'ERROR'},
    }
})

# Command line arguments: -p/--path for target path, -d/--db for database file
parser = argparse.ArgumentParser(description='Build music DB from mp3 files')
parser.add_argument('-p', '--path', required=True, help='Path to search for mp3 files')
parser.add_argument('-d', '--db', default='./myMusic.db', help='SQLite database file to use')
args = parser.parse_args()


def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()
 
def createTable(cursor_obj):
    logging.info("CREATE TABLE IF NOT EXISTS")
    table = """ CREATE TABLE IF NOT EXISTS TRACKS  (
                fullpath	VARCHAR(255) NOT NULL,
                sha256  VARCHAR(64) NOT NULL,
                folder	VARCHAR(255) NOT NULL,
                filename	VARCHAR(255) NOT NULL,
                artist	VARCHAR(255),
                title	VARCHAR(255),
                album	VARCHAR(255),
                genre	VARCHAR(255),
                CONSTRAINT filepath PRIMARY KEY(fullpath)
            ); """
    cursor_obj.execute(table)
    table = """CREATE TABLE IF NOT EXISTS  genre_API (
        tag1 VARCHAR(255), 
        tag2 VARCHAR(255), 
        artist VARCHAR(255));"""
    cursor_obj.execute(table)

def AddEntry(cursor_obj,fullpath, sha256, path, file, artist,title, album, genre):
    conn.execute('''INSERT or IGNORE INTO TRACKS (fullpath,sha256, folder, filename, artist,title,album, genre)
                    VALUES (?,?,?,?,?,?,?,?)''',    (fullpath, sha256, path, file, artist,title, album, genre))
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
        return ''
    #retStr = ''.join(filter(str.isalnum, MyStr))
    retStr = re.sub(r'[^a-zA-Z0-9éèàç&êöë \-]', ' ', MyStr)
    retStr = retStr.title()
    return str(retStr)

def GetfromMp3(fullfile):
    logging.debug("Check MP3 tags for %s", fullfile)
    mp3info= {}
    try:
        audio = eyed3.load(fullfile)
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
    
def getTag(myArtist):
    tagArr = []
    logging.debug("Get tag for artist %s", myArtist)
    payload = {'artist': myArtist, 'autocorrect' : 1 , 'format': 'json', 'user': 'RJ', 'api_key': 'b25b959554ed76058ac220b7b2e0a026'}
    r = requests.get("https://ws.audioscrobbler.com/2.0/?method=artist.gettopTags", params=payload)
    try:
        if 'toptags' in r.json().keys():
            respDic = r.json()['toptags']['tag'][:2]
            for myTag in respDic:
                tagArr.append(myTag['name'])
    except Exception as e:
        logging.error("Error getting tags for artist %s : %s", str(myArtist), str(e))  
    return tagArr


def artistExists(artistName):
    artistName = str(artistName)
    logging.debug("Looking for artist %s", artistName)
    QueryCurs.execute("SELECT * FROM genre_API where artist = ?",(artistName,))
    result = QueryCurs.fetchone()
    if  result:
        return result[0]
    else:
        return False
    
def updateArtise(newArtist):
    sql = ''' INSERT INTO genre_API (tag1, tag2, artist) VALUES (?,?,?)'''
    QueryCurs.execute(sql, newArtist)
    conn.commit()
    logging.info("NEW artist (%s) tags (%s) (%s)", newArtist[2], newArtist[0], newArtist[1])


def check_artist(artistName):
    if artistExists(artistName):
        logging.debug('   Found artist %s', artistName)
        return True
    else:
        tagArray =getTag(artistName)
        if len(tagArray) == 2:
            updateArtise((tagArray[0], tagArray[1], artistName))
        elif len(tagArray) == 1:
            updateArtise((tagArray[0], '', artistName))
        else:
            logging.debug("No data, no update for artist %s", artistName)


def get_already_done():
    done_dict = {}
    QueryCurs.execute("SELECT fullpath FROM TRACKS")
    rows = QueryCurs.fetchall()
    for row in rows:
        done_dict[row[0]] = True
    logging.info("Already done files: %s", len(done_dict))
    return done_dict

def generateArtistGenre(QueryCurs, big_list, done_songs):
    cpt = 0
    for song in big_list:
        cpt += 1
        if str(song) not in done_songs.keys():
            insertArtist = GetfromMp3(song)
            sha256 = sha256sum(song)
            myArtist = myTitle = myAlbum  = myGenre  =''
            myFolder = str(song.parent)
            myFile = str(song.name)
            myFull = str(song)
            if insertArtist:
                if 'artist' in insertArtist.keys():
                    myArtist = insertArtist['artist']
                    check_artist(myArtist)
                if 'title' in insertArtist.keys():
                    myTitle  = insertArtist['title']
                if 'album' in insertArtist.keys():
                    myAlbum  = insertArtist['album']
                if 'genre' in insertArtist.keys():
                    myGenre  = insertArtist['genre']
            logging.info("(%s / %s )  %s ART %s GENRE %s (%s)", cpt, len(big_list), myTitle, myArtist, myGenre, myFile)
            AddEntry(QueryCurs,myFull, sha256, myFolder, myFile,  myArtist, myTitle, myAlbum, myGenre)
        else:
            logging.debug("(%s / %s ) SKIP  done file %s",  cpt, len(big_list), str(song))


conn = sqlite3.connect(args.db)
QueryCurs = conn.cursor()
createTable(QueryCurs)
logging.info("Database connected: %s", args.db)
done_songs = get_already_done()
global_Todo =  get_all_path(args.path)
logging.info("BIG LIST : %s", len(global_Todo))
generateArtistGenre(QueryCurs, global_Todo, done_songs)

# curl "https://ws.audioscrobbler.com/2.0/?method=artist.gettopTags&artist=indochine&user=RJ&api_key=b25b959554ed76058ac220b7b2e0a026&format=json"

