"""Download files from an ORA collection

See https://ora.ox.ac.uk/

This script makes one API call to get the list of files to download.

Then it uses the "download_url" and "name" of each file to download and save to
the working directory.
"""
import argparse
import json
import os
import sys

import requests


def ora_get(args=None):
    parser = argparse.ArgumentParser(prog="ora_get")
    parser.add_argument(
        "collection_id",
        type=str,
        help="Pass the UUID of the collection to download",
    )
    args = parser.parse_args(args)

    try:
        collection_meta = search(args.collection_id)
    except Exception as e:
        print("No results", e)
        sys.exit()

    save_collection_meta(args.collection_id, collection_meta)
    download_collection_files(args.collection_id, collection_meta)


def search(collection_id):
    url = f"https://ora.ox.ac.uk/objects/uuid:{collection_id}.json"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def save_collection_meta(collection_id, collection_meta):
    fname = f"metadata_{collection_id}.json"
    print("Saving metadata to", fname)
    with open(fname, "w") as fd:
        json.dump(collection_meta, fd, indent=2)


def download_collection_files(collection_id, collection_meta):
    collection_files = json.loads(
        collection_meta["response"]["document"]["display__binary_files"]
    )
    for file_meta in collection_files:
        fname = file_meta["filename"]
        if os.path.exists(fname):
            print("Skipping", fname)
        else:
            print("Downloading", fname)
            save_file(collection_id, file_meta)


def save_file(collection_id, file_meta):
    file_id = file_meta["file_admin_hyrax_filesest_identifier"]
    file_url = f"https://ora.ox.ac.uk/objects/uuid:{collection_id}/files/{file_id}"
    r = requests.get(file_url, stream=True)
    with open(file_meta["filename"], "wb") as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
