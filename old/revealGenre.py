import requests
import sqlite3
import logging
import time

conn = sqlite3.connect("./myMusic_042024.db")
cur = conn.cursor()

def getTag(myArtiste):
    tagArr = []
    payload = {'artist': myArtiste, 'autocorrect' : 1 , 'format': 'json', 'user': 'RJ', 'api_key': 'b25b959554ed76058ac220b7b2e0a026'}
    r = requests.get("https://ws.audioscrobbler.com/2.0/?method=artist.gettopTags", params=payload)
    if 'toptags' in r.json().keys():
        respDic = r.json()['toptags']['tag'][:2]
        for myTag in respDic:
            tagArr.append(myTag['name'])
    return tagArr

def updateArtise(newArtist):
    sql = ''' UPDATE genre_API
              SET tag1 = ? ,UPDATE
                  tag2 = ?
              WHERE artist = ?'''
    cur.execute(sql, newArtist)
    conn.commit()
    logging.info("Update done")


def getArtisteTodo():
    artistArr = []
    cur.execute("SELECT * FROM genre_API where tag1 is null")
    rows = cur.fetchall()
    for row in rows:
        artistArr.append(row)
    return artistArr

artisteTodo = getArtisteTodo()
for myArtiste in artisteTodo:
    tagArray = getTag(myArtiste[0])
    logging.info("%s %s", myArtiste[0], tagArray)
    if len(tagArray) == 2:
        updateArtise((tagArray[0], tagArray[1], myArtiste[0]))
    elif len(tagArray) == 1:
        updateArtise((tagArray[0], '', myArtiste[0]))
    else:
        logging.info("No data, no update")
    time.sleep(3)

