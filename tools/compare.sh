#!/bin/sh
# usage: compare.sh <label>  — rebuild and diff against saved baseline
set -e
SITE=$(basename "$(cd "$(dirname "$0")/.." && pwd)")
rm -rf public
hugo --baseURL / --quiet
# normalize build-to-build noise before diffing:
#   - asset fingerprint hashes, which change whenever the asset does
#   - Hugo's shortcode placeholder counter. When a heading contains a shortcode
#     (e.g. `#### Module 1: {{<modname 1>}}`), the id is generated from the raw
#     text, so the placeholder token lands in the id — and the counter is not
#     stable across builds, so those ids differ every run even with no changes.
normalize() {
	find "$1" -name '*.html' -exec sed -i.bak -E \
		-e 's/\.[0-9a-f]{40,128}\.(css|js)/.HASH.\1/g' \
		-e 's/hahahugoshortcode[0-9]+s/hahahugoshortcodeNs/g' {} \;
	find "$1" -name '*.bak' -delete
}
cp -R public /tmp/candidate.$$ && normalize /tmp/candidate.$$
cp -R "/tmp/golden-$SITE-$1" /tmp/golden.$$ && normalize /tmp/golden.$$
diff -r --exclude='*.css' --exclude='*.js' /tmp/golden.$$ /tmp/candidate.$$ && echo "HTML: IDENTICAL"
rm -rf /tmp/candidate.$$ /tmp/golden.$$
