from requests_html import HTMLSession
from bs4 import BeautifulSoup
import argparse
import json 
import pandas as pd

def get_imdb_metadata(imdb_id):

    session = HTMLSession()
    request = session.get(f"https://www.imdb.com/title/{imdb_id}/")
    html = request.text
    soup = BeautifulSoup(html, "lxml")

    return json.loads("".join(soup.find("script", {"type":"application/ld+json"}).contents))

def summarize_metadata(metadata):

    summarized_metadata = {}
    summarized_metadata['name'] = metadata.get('name', None)
    summarized_metadata['poster'] = metadata.get('image', None)
    summarized_metadata['description'] = metadata.get('description', None)
    summarized_metadata['rating'] = metadata.get('aggregateRating', {}).get('ratingValue', None)
    summarized_metadata['release'] = metadata.get('datePublished', None)
    summarized_metadata['genre'] = '; '.join(metadata.get('genre', []))

    actors_list = []
    
    for actor in metadata.get('actor', []):
      actors_list.append(actor['name'])
    
    summarized_metadata['actors'] = '; '.join(actors_list)

    return summarized_metadata

def main():

    argument_parser = argparse.ArgumentParser(about='imdb-metadata-extractor: a tool to extract movie metadata from IMDB')
    argument_parser.add_argument('imdb_id', help='IMDB ID of the movie')
    argument_parser.add_argument('--output', help='output file')
    argument_parser.add_argument('--format', help='output format', default='csv', choices=['json', 'csv', 'xlsx'])
    arguments = argument_parser.parse_args()

    try:
        metadata = get_imdb_metadata(arguments.imdb_id)
    except:
        print('ERROR: Unable to get movie metadata')
        exit(1)
    
    summarized_data = summarize_metadata(metadata)

    if not arguments.output:
        print(json.dumps(summarized_data, indent=4))

    elif arguments.format == 'json':
        with open(arguments.output, 'w') as writer:
            writer.write(json.dumps(summarized_data, indent=4))

    elif arguments.format == 'csv':
        pd.DataFrame([summarized_data]).to_csv(arguments.output, index=False)

    elif arguments.format == 'xlsx':
        pd.DataFrame([summarized_data]).to_excel(arguments.output, index=False)
    
if __name__ == '__main__':
    main()