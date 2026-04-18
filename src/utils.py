import pathlib
import re, logging
import hashlib


def get_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


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
    return resource_dict


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
    return resource_dict




def decade_from_date(date):
    if isinstance(date, str):
        match = re.search(r'(\d{4})', date)
        if match:
            year = int(match.group(1)) +1
            decade = (year // 10) * 10
            return f"{decade}s"[3:]
    elif hasattr(date, 'year'):
        year = date.year + 1
        decade = (year // 10) * 10
        return f"{decade}s"[3:]
    return ''

def clStr(MyStr):
    if MyStr == '' or MyStr is None:
        return ''
    retStr = re.sub(r'[^a-zA-Z0-9éèàç&êöë \-]', ' ', MyStr)
    retStr = retStr.replace('www', '').replace('webm', '').replace('slider', '').replace('youtube', '').replace('  ', ' ')
    retStr = retStr.replace('official', '').replace('officiel', '').replace('clip', '').replace('kz', '') 
    #retStr = retStr.title()
    retStr = retStr.lower()
    return str(retStr)

def get_all_mp3_files(pathInput):
    Todo = []
    for path in pathlib.Path(pathInput).rglob('*.mp3'):
        if path.is_file() :
            Todo.append(path)
    return Todo


def write_genre(artist, genre,mode):
    #wrtite to file log
    write_str= f"{genre}\t{artist}\t{mode}\n"
    open('db/genre_res2.txt', 'a').write(write_str)

def get_year_mb(artist_name, mb_dict):
    if artist_name in mb_dict and 'decade' in mb_dict[artist_name]:
        return mb_dict[artist_name]['decade']
    return None

