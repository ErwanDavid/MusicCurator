from utils import clStr
import logging

def load_ressource_json(file_path):
    import json
    resource_dict = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            try:
                obj = json.loads(line)
                for key, value in obj.items():
                    resource_dict[key.lower()] = value
            except json.JSONDecodeError as e:
                logging.error("Error decoding JSON line: %s, error: %s", line, str(e))
    logging.info("JSON artists loaded: %s", len(resource_dict))
    return resource_dict


def write_genre(artist, genre,mode):
    #wrtite to file log
    write_str= f"{genre}\t{artist}\t{mode}\n"
    open('db/genre_res2.txt', 'a').write(write_str)

def get_year_mb(artist_name, mb_dict):
    if artist_name in mb_dict and 'decade' in mb_dict[artist_name]:
        return mb_dict[artist_name]['decade']
    return None

def load_ressource(file_path):
    resource_dict = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('\t')
                if len(parts) == 1:
                    artist_name = parts[0].strip().lower()
                    resource_dict[artist_name] = 1
                elif len(parts) == 2:
                    artist_name = parts[0].strip().lower()
                    genre = parts[1].strip().lower()
                    resource_dict[artist_name] = genre
                elif len(parts) >= 3:
                    genre_tab = []
                    genre_tab.append(parts[0].strip().lower())
                    genre_tab.append(parts[1].strip().lower())
                    genre_tab.append(parts[2].strip().lower())
                    genre_tab.append(parts[3].strip().lower())
                    genre_tab.sort(key=lambda x: len(x))
                    artist_name = parts[4].strip().lower()
                    count = parts[5].strip().lower()
                    resource_dict[artist_name] = (genre_tab[0], genre_tab[1], genre_tab[2], genre_tab[3], count)
    logging.info("      loaded: %s", len(resource_dict))
    return resource_dict

def get_artist_genre(artist, curated_dict, api_dict, mb_dict, allow_genre):
    artist_name = artist['artist'].lower()
    logging.debug("   Getting genre for artist: %s", artist_name)
    if artist_name in curated_dict:
        logging.debug("   found curated genre for artist: %s", artist_name)
        write_genre(artist_name, curated_dict[artist_name], "curated")
        return curated_dict[artist_name], get_year_mb(artist_name, mb_dict)
    elif artist_name in api_dict:
        genres = api_dict[artist_name]
        logging.debug("   found API genre for artist: %s, genre: %s", artist_name, genres)
        for genre in genres:
             logging.debug("   Checking genre: %s", genre)
             if genre in allow_genre:
                logging.debug("   genre allowed: %s", allow_genre[genre])
                write_genre(artist_name, allow_genre[genre], "api")
                return allow_genre[genre], get_year_mb(artist_name, mb_dict)
        logging.info("   No allowed genre found for artist: %s, API genres: %s", artist_name, genres)
    elif artist_name in mb_dict:
        genres = mb_dict[artist_name]['genres']
        logging.debug("   found MB genre for artist: %s, genre: %s", artist_name, genres)
        if genres in allow_genre:
            logging.debug("   genre allowed: %s", allow_genre[genres])
            write_genre(artist_name, allow_genre[genres], "mb")
            return allow_genre[genres], get_year_mb(artist_name, mb_dict)
        logging.info("   No allowed genre found for artist: %s, MB genres: %s", artist_name, genres)
    elif 'genre' in artist:
        if artist['genre'] in allow_genre:
            logging.debug("   genre from tag allowed: %s", allow_genre[artist['genre']])
            write_genre(artist_name, allow_genre[artist['genre']], "tag")
            return allow_genre[artist['genre']], get_year_mb(artist_name, mb_dict)
        logging.info("   No genre found for artist: %s", artist_name)    
    else:
        write_genre(artist_name, "unknown", "unknown")
        return None, None
    write_genre(artist_name, "unknown", "unknown")
    return None, None