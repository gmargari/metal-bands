from requests_html import HTMLSession
from requests_html import HTML
import codecs
import json
import sys
import re
import os
import csv
import time

OUTPUT_DIR = 'data'
session = HTMLSession()

#===============================================================================
# throttle ()
#===============================================================================
def throttle():
    sleep_time = 3  # based on their robots.txt
    time.sleep(sleep_time)

#===============================================================================
# get_html ()
#===============================================================================
def get_html(url):
    print('\t\t\t\t%s' % (url))
    throttle()
    return session.get(url).html

#===============================================================================
# get_valid_filename ()
#===============================================================================
# from https://github.com/django/django/blob/master/django/utils/text.py
def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

#===============================================================================
# save_dict_to_file ()
#===============================================================================
def save_dict_to_file(d, filename):
    with codecs.open(filename, 'w', 'utf-8') as f:
        print(json.dumps(d, indent=2), file=f)

#===============================================================================
# get_album_songs ()
#===============================================================================
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

#===============================================================================
# get_band_similar_bands ()
#===============================================================================
def get_band_similar_bands(band_id):
    url = 'https://www.metal-archives.com/band/ajax-recommendations/id/%s' % (band_id)
    html = get_html(url)
    bands = []
    for row in html.find('tr')[1:]:
        cells = row.find('td')
        band_name = cells[0].text
        if band_name.startswith('No similar artist'):
            continue
        if band_name.startswith('(see more)'):
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

#===============================================================================
# get_band_info ()
#===============================================================================
def get_band_info(band_url):
    html = get_html(band_url)
    info = html.find('#band_stats')[0]
    dt = [ x.text.lower().rstrip(':') for x in info.find('dt') ]
    dd = [ x.text for x in info.find('dd') ]
    return dict(zip(dt, dd))

#===============================================================================
# get_band_albums ()
#===============================================================================
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

#===============================================================================
# band ()
#===============================================================================
class Band:
    def __init__(self):
        self.info = {}

    def parse_basic_info(self, line):
        # TODO: country, genre, status not needed,
        # they are included in info['info']
        info = self.info
        info['name'] = HTML(html=line[1]).text
        info['url'] = HTML(html=line[1]).absolute_links.pop()
        info['id'] = info['url'][info['url'].rfind('/')+1:]
        info['country'] = line[2]
        info['genre'] = line[3]
        info['status'] = HTML(html=line[4]).text

    def extend_info(self):
        info = self.info
        info['info'] = get_band_info(info['url'])
        info['albums'] = get_band_albums(info['id'])
        info['similar_bands'] = get_band_similar_bands(info['id'])

    def save_on_disk(self):
        info = self.info
        filename = self._filename()
        save_dict_to_file(info, filename)

    def already_saved_on_disk(self):
        filename = self._filename()
        return os.path.isfile(filename)

    def _filename(self):
        info = self.info
        filename = '%s.%s.json' % (info['name'], info['id'])
        filename = get_valid_filename(filename)
        return '%s/%s' % (OUTPUT_DIR, filename)

    def name(self):
        return self.info['name']

#===============================================================================
# download_bands ()
#===============================================================================
def download_bands(filename):
    with codecs.open(filename, 'r', 'utf-8') as f:
        next(f)  # skip header line
        csvreader = csv.reader(f, delimiter=',', skipinitialspace=True)
        for line in csvreader:
            band = Band()
            band.parse_basic_info(line)

            if band.already_saved_on_disk():
                print('%s: skipping (already downloaded)' % band.name())
                continue

            print('%s' % band.name())
            band.extend_info()
            band.save_on_disk()

#==============================================================================
# main ()
#==============================================================================
def main():
    if len(sys.argv) != 2:
        print('Syntax: %s <MA-band-names_XXXX-XXX-XX.csv>' % sys.argv[0])
        sys.exit(1)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    infile = sys.argv[1]
    download_bands(infile)

if __name__ == '__main__':
    main()