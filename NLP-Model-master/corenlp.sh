#!/bin/bash

set -e

# By default download to the data directory
DOWNLOAD_PATH="./data/corenlp"
echo "Will download to: $DOWNLOAD_PATH"

# Download zip, unzip
pushd "/tmp" 
wget -O "stanford-corenlp-full-2017-06-09.zip" "http://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip"
unzip "stanford-corenlp-full-2017-06-09.zip"
rm "stanford-corenlp-full-2017-06-09.zip"
popd

# Put jars in DOWNLOAD_PATH
mkdir -p "$DOWNLOAD_PATH"
mv "/tmp/stanford-corenlp-full-2017-06-09/"*".jar" "$DOWNLOAD_PATH/"

echo "Download completed...!!"
