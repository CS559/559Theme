#!/bin/sh
# usage: baseline.sh <label>   — builds and snapshots public/ for comparison
set -e
SITE=$(basename "$(cd "$(dirname "$0")/.." && pwd)")
rm -rf public
hugo --baseURL / --quiet
rm -rf "/tmp/golden-$SITE-$1" && cp -R public "/tmp/golden-$SITE-$1"
echo "baseline saved: /tmp/golden-$SITE-$1"
