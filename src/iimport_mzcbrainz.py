import argparse
import json
import pprint as pp
from utils import clStr, decade_from_date

parser = argparse.ArgumentParser(description='Build music DB from mp3 files')
parser.add_argument('-j', '--json', required=True, help='Path to JSON file')
args = parser.parse_args()

field_of_interest = ['name', 'tags', 'life-span', 'genres', 'gender', 'rating', 'aliases']

def get_best_tag(tags):
    if not tags:
        return None
    best_tag = max(tags, key=lambda x: x.get('count', 0))
    return best_tag['name'] if 'name' in best_tag else None

def get_score_from_rating(rating):
    score = rating.get('value', 0)
    if score and score >= 4:
        tot_score = score * rating.get('votes-count', 0)
        return tot_score
    return None

with open(args.json) as f:
    for line in f:
        myObj = json.loads(line)
        intersting = {k: myObj[k] for k in field_of_interest if k in myObj}
        #pp.pprint(intersting)
        final={}
        name = clStr(intersting['name'])
        final[name] = {}
        if 'genres' in intersting:
            final[name]['genres'] = clStr(get_best_tag(intersting['genres']))
        elif 'tags' in intersting and len(intersting['tags']) > 0:
            final[name]['genres'] = clStr(get_best_tag(intersting['tags']))
        if final[name]['genres']:
            if 'life-span' in intersting and 'begin' in intersting['life-span']:
                final[name]['life-span'] = intersting['life-span']['begin']
                final[name]['decade'] = decade_from_date(intersting['life-span']['begin'])
            if 'rating' in intersting and len(intersting['rating']) > 0 :
                final[name]['rating'] = get_score_from_rating(intersting['rating'])
            print(json.dumps(final))
