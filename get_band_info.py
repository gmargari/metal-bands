from requests_html import HTMLSession
import codecs
import json
import sys
import re
import os
import csv
import time

outdir = 'data'
session = HTMLSession()

def throttle():
    sleep_time = 3  # based on their robots.txt
    time.sleep(sleep_time)

def get_html(url):
    print('\t\t\t\t%s' % (url))
    throttle()
    return session.get(url).html

def save_to_file(bands, filename):
    with codecs.open(filename, 'w', 'utf-8') as f:
        print(json.dumps(bands, indent=2), file=f)

def get_album_songs(album_url):
    throttle()

    html = get_html(album_url)
    songs = []
    for row in html.find('table.table_lyrics')[0].find('tr')[0:]:
        cells = row.find('td')
        if cells[0].text:
            if len(cells) > 2:
                song_number = cells[0].text
                song_name = cells[1].text
                song_duration = cells[2].text
                song = [
                    song_number,
                    song_name,
                    song_duration,
                ]
            else:
                song = cells[0].text
            songs.append(song)
    return songs

def get_band_similar_bands(band_id):
    url = 'https://www.metal-archives.com/band/ajax-recommendations/id/%s' % (band_id)
    html = get_html(url)
    bands = []
    for row in html.find('tr')[1:]:
        cells = row.find('td')
        band_name = cells[0].text
        if band_name.startswith('No similar artist'):
            continue
        band_country = cells[1].text
        band_genre = cells[2].text
        band_score = cells[3].text
        band = {
            'name': band_name,
            'country': band_country,
            'genre': band_genre,
            'score': band_score,
        }
        bands.append(band)
    return bands

def get_band_info(band_url):
    html = get_html(band_url)
    info = html.find('#band_stats')[0]
    dt = [ x.text.lower() for x in info.find('dt') ]
    dd = [ x.text for x in info.find('dd') ]
    return dict(zip(dt, dd))

def get_band_albums(band_id):
    album_type = 'all'  # 'all': all releases, 'main': full-length albums
    url = 'https://www.metal-archives.com/band/discography/id/%s/tab/%s' % (band_id, album_type)
    html = get_html(url)
    albums = []
    for row in html.find('tr')[1:]:
        cells = row.find('td')
        album_name = cells[0].text
        print('\t%s' % album_name)
        if album_name.startswith('Nothing entered yet'):
            continue
        album_url = list(cells[0].absolute_links)[0]
        # album_id = album_url[album_url.rfind('/')+1:]
        album_type = cells[1].text
        album_year = cells[2].text
        album_songs = get_album_songs(album_url)
        album = {
            'name': album_name,
            'url': album_url,
            'type': album_type,
            'year': album_year,
            'songs': album_songs,
        }
        albums.append(album)
    return albums

def bands_csv_to_json(filename):
    with codecs.open(filename, 'r', 'utf-8') as f:
        next(f)  # skip header line
        csvreader = csv.reader(f, delimiter=',', skipinitialspace=True)
        bands = []
        for line in csvreader:
            band_name = re.findall(r'>(.*)<', line[1])[0]
            print(band_name)
            band_url = re.findall(r'href=\'(.*)\'', line[1])[0]
            band_id = band_url[band_url.rfind('/')+1:]
            band_country = line[2]
            band_genre = line[3]
            band_status = re.findall(r'>(.*)<', line[4])[0]
            band = {
                'name': band_name,
                'url': band_url,
                'id': band_id,
                # >>>>> not needed: included in 'info' below
                'country': band_country,
                'genre': band_genre,
                'status': band_status,
                # <<<<< not needed: included in 'info' below
                'info': get_band_info(band_url),
                'albums': get_band_albums(band_id),
                'similar_bands': get_band_similar_bands(band_id),
            }
            # bands.append(band)

            ##### For now save periodically each band, in case we crash (or maybe dictionary becomes to large? OOM?!)
            band_name = band_name.replace('/', '-`')
            band_name = band_name.replace(':', '.')
            save_to_file(band, '%s/%s.json' % (outdir, band_name))

    return bands

#==============================================================================
# main ()
#==============================================================================
def main():
    if len(sys.argv) != 2:
        print('Syntax: %s <MA-band-names_XXXX-XXX-XX.csv>' % sys.argv[0])
        sys.exit(1)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    infile = sys.argv[1]
    bands = bands_csv_to_json(infile)
    # save_to_file(bands, infile.replace('.csv', '.json'))

if __name__ == '__main__':
    main()