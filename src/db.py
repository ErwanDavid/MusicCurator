import sqlite3
import logging
import os

def execute_query(query, dbfile,  params=None):
    import sqlite3
    conn = sqlite3.connect(dbfile)
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    conn.commit()
    conn.close()

def init_db(dbfile):
    create_table_query = '''CREATE TABLE IF NOT EXISTS music (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            path TEXT,
                            md5 TEXT,
                            artist TEXT,
                            title TEXT,
                            album TEXT,
                            genre TEXT,
                            year TEXT,
                            decade TEXT,
                            genre_calc TEXT,
                            decade_artist TEXT,
                            genre_src TEXT,
                            popularity TEXT,
                            nb_views INTEGER
                        )'''
    execute_query(create_table_query, dbfile) 
      
def insert_file_info_to_database(mp3_file, mp3_info, dbfile):
    insert_query = '''INSERT INTO music (path, md5, artist, title, album, genre, year, decade, genre_calc, decade_artist, genre_src, popularity, nb_views) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    values = (str(mp3_file), mp3_info.get('md5', ''), mp3_info.get('artist', ''), mp3_info.get('title', ''), mp3_info.get('album', ''), mp3_info.get('genre', ''), mp3_info.get('year', ''), mp3_info.get('decade', ''), mp3_info.get('genre_calc', ''), mp3_info.get('decade_artist', ''), mp3_info.get('genre_src', ''), mp3_info.get('popularity', ''), mp3_info.get('nb_views', 0))
    execute_query(insert_query, dbfile, values)
