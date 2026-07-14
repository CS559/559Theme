#!/bin/sh
# usage: compare.sh <label>  — rebuild and diff against saved baseline
set -e
SITE=$(basename "$(cd "$(dirname "$0")/.." && pwd)")
rm -rf public
hugo --baseURL / --quiet
# normalize asset fingerprint hashes before diffing
normalize() { find "$1" -name '*.html' -exec sed -i.bak -E 's/\.[0-9a-f]{40,128}\.(css|js)/.HASH.\1/g' {} \; ; find "$1" -name '*.bak' -delete; }
cp -R public /tmp/candidate.$$ && normalize /tmp/candidate.$$
cp -R "/tmp/golden-$SITE-$1" /tmp/golden.$$ && normalize /tmp/golden.$$
diff -r --exclude='*.css' --exclude='*.js' /tmp/golden.$$ /tmp/candidate.$$ && echo "HTML: IDENTICAL"
rm -rf /tmp/candidate.$$ /tmp/golden.$$
