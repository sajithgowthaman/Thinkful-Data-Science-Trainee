
"""A script to read in and store documents in a sqlite database."""

import json
import os
import sqlite3

from tqdm import tqdm

import utils



class BuildingDB(object):
    def __init__(self, data_path, save_path):
        self.data_path = data_path
        self.save_path = save_path
        self.files = [self.data_path]

    def store_contents(self, ):
        if os.path.isfile(self.save_path):
            print('%s already exists! Not overwriting.' % self.save_path)
            os.remove(self.save_path)

        print('Reading into database...')
        conn = sqlite3.connect(self.save_path)
        c = conn.cursor()
        c.execute("CREATE TABLE documents (id PRIMARY KEY, text);")

        count = 0
        with tqdm(total=len(self.files)) as pbar:
            for pairs in tqdm(map(self.get_contents, self.files)):
                count += len(pairs)
                c.executemany("INSERT OR IGNORE INTO documents VALUES (?,?)", pairs)
                pbar.update()

        print('Read %d docs.' % count)
        print('Committing...')
        conn.commit()
        conn.close()

    @staticmethod
    def get_contents(filename):
        """Parse the contents of a file. Each line is a JSON encoded document."""
        _documents = []
        with open(filename) as f:
            for line in f:
                # Parse document
                doc = json.loads(line)
                # Skip if it is empty or None
                if not doc:
                    continue
                # Add the document
                _documents.append((utils.normalize(doc['id']), doc['text']))
        return _documents
