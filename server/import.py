#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
import argparse
import time
import math

# read from settings.py
URL_PREFIX = 'rest'
API_VERSION = 'v1'
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = '5000'

SERVER_HOST = os.environ.get('SERVER_HOST', DEFAULT_HOST)
SERVER_PORT = int(os.environ.get('SERVER_PORT', DEFAULT_PORT))
DEFAULT_ENTRY_POINT = '%s:%s/%s/%s' % (SERVER_HOST, SERVER_PORT, URL_PREFIX, API_VERSION)
BATCH_SIZE = 100

#===============================================================================
# perform_post ()
#===============================================================================
def perform_post(entry_point, resource, data):
    headers = {'Content-Type': 'application/json'}
    post_data = json.dumps(data)
    return requests.post(endpoint(entry_point, resource), post_data, headers=headers)

#===============================================================================
# perform_delete ()
#===============================================================================
def perform_delete(entry_point, resource):
    return requests.delete(endpoint(entry_point, resource))

#===============================================================================
# get_inserted_ids ()
#===============================================================================
def get_inserted_ids(r):
    ids = []
    if (r.status_code == 201):
        response = r.json()
        if (response['_status'] == 'OK'):
            # If we inserted multiple items
            if ('_items' in response):
                for item in response['_items']:
                    if (item['_status'] == "OK"):
                        ids.append(item['_id'])
            # We inserted a single item
            else:
                ids.append(response['_id'])

    return ids

#===============================================================================
# endpoint ()
#===============================================================================
def endpoint(entry_point, resource):
    return 'http://%s/%s/' % (entry_point, resource)

#===============================================================================
# error ()
#===============================================================================
def error(message):
    print(message)
    sys.exit(1)

#===============================================================================
# create_arg_parser ()
#===============================================================================
def create_arg_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-E', metavar='ENTRY_POINT', help="REST API entry point", default=DEFAULT_ENTRY_POINT, type=str)
    parser.add_argument('F', metavar='FILENAME', help="file(s) to import", type=str, nargs='+')
    parser.add_argument('-d', '--drop-col', help="drop collection(s) before import", action='store_true', default=False)
    return parser

#===============================================================================
# preprocess_band_data ()
#===============================================================================
def preprocess_band_data(band):
    albums_new = []
    for album in band['albums']:
        # An album will most probably have one disk, but may have many disks
        # Transform
        # songs: [
        #    "Disk A",
        #     [ "1.", "Hate", "2:37" ],
        #     [ "1.", "Fear", "2:37" ],
        #    "Disk B",
        #     [ "1.", "Hate 2", "2:37" ],
        #     [ "1.", "Fear 2", "2:37" ],
        # ]
        # to
        # songs: [
        #     [
        #         [ "1.", "Hate", "2:37" ],
        #         [ "1.", "Fear", "2:37" ],
        #     ],
        #     [
        #         [ "1.", "Hate 2", "2:37" ],
        #         [ "1.", "Fear 2", "2:37" ],
        #     ]
        # ]
        disks = []
        disk = []
        for song in album['songs']:
            if isinstance(song, list):
                disk.append(song)
            else:
                # New disk etc. Start new subalbum
                assert isinstance(song, str)
                disks.append(disk)
                disk = []
        assert disk
        disks.append(disk)
        album['songs'] = disks

#===============================================================================
# main ()
#===============================================================================
def main():
    parser = create_arg_parser()
    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    entry_point = args.E
    infiles = args.F
    drop_collection = args.drop_col

    # os.environ['TZ'] = 'UTC'
    # time.tzset()

    for infile in infiles:
        with open(infile) as f:

            data_list = json.loads(f.read())

            collection = 'bands'

            # Drop collection, if required
            if (drop_collection):
                r = perform_delete(entry_point, collection)
                print("Dropped collection '%s', status code: %s" % (collection, r.status_code))
                if r.status_code != 204:
                    error(json.dumps(r.json(), indent=2))

            for data in data_list:
                print(data['name'])
                # Post data to collection
                preprocess_band_data(data)
                r = perform_post(entry_point, collection, data)
                if r.status_code != 201:
                    if '_items' in r.json():
                        errors = r.json()['_items']
                    else:
                        errors = [ r.json() ]
                    for idx, val in enumerate(errors):
                        if (val["_status"] != "OK"):
                            print("Error: could not insert\n%s" % (json.dumps(data, indent=4)))
                            print("because\n%s\n" % (json.dumps(val['_issues'], indent=4)))
                    error(r.json()['_error']['message'])
                # break
if __name__ == "__main__":
    main()
