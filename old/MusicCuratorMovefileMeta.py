import sqlite3
import shutil
import eyed3
import logging
from pathlib import Path

conn = sqlite3.connect("./myMusic_052024c.db")
cur = conn.cursor()

def getTracksTodo():
    artistArr = []
    cur.execute('''select t.fullpath, t.filename, t.artist, t.title, g.final_tag  from TRACKS t, genre_MAP g
                    where g.artiste = t.artist ''')
    rows = cur.fetchall()
    for row in rows:
        artistArr.append(row)
    return artistArr


def SetId3forMP3(fullfile, artist, title, genre):
    audio = eyed3.load(fullfile)
    #print("___mp3 tag", audio.tag.artist)
    logging.debug("Check ID3 for %s", fullfile)
    if not audio:
        logging.info("Set tag to %s artist %s title %s", fullfile, artist, title)
        audio.initTag()
        audio.tag.artist = artist
        audio.tag.title = title
        audio.tag.genre = genre 
        audio.tag.save()
    else:
        if len(str(audio.tag.title)) < 1:
            logging.info("Set tag to %s artist %s title %s", fullfile, artist, title)
            audio.initTag()
            audio.tag.artist = artist
            audio.tag.title = title
            audio.tag.genre = genre 
            audio.tag.save()


tracksTodo = getTracksTodo()
for myTrack in tracksTodo:
    fullpath = myTrack[0]
    name = myTrack[1]
    artist = myTrack[2]
    title = myTrack[3]
    genre = myTrack[4]
    if genre:
        if len(genre) < 1:
            genre = 'other'
    else:
        genre = 'other'
    genre = genre.title()
    destFolder = Path("/volume1/Share/MP3_Classe/sorted/" + genre + "/" + artist)
    if not destFolder.exists():
        destFolder.mkdir(parents=True)
    dst = str(destFolder) + '/' + artist + '_' + title + '.mp3'
    destFile = Path(dst)
    if not destFile.exists():
        SetId3forMP3(fullpath, artist, title, genre)
        try:
            shutil.copyfile(fullpath, dst)
            logging.info("CP ok %s --> %s", fullpath, dst)
        except:
            logging.error("Error in cp %s --> %s", fullpath, dst)
    else:
        logging.info("DONE %s --> %s", fullpath, dst)