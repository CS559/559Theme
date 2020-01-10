# CS559 Theme

A theme created by Michael Gleicher to make a class web page.

This builds on the "MainRoad" theme - it needs to be "mixed in" to that theme.in the config.toml file, have the line
````toml
theme = ["559Theme","mainroad"]
````
and make sure that both mainroad and 559Theme are in the themes directory

- New variables for tuning:
    - noheader - set to true on a page to skip the header (default/baseof.html)
    - myreadmore - true (by default) for a less obnoxious read me in a summary (and a link if the summary is the whole page)

Changes (not exhaustive):
- Add Section summaries to page list summaries (default/list.html)
- Add lunr search (content/lunr-search, widgets/lunr, index.json)
- A taglist for post_meta
- Put the logo in the header (assets/svg, partials/header)
- New widgets
    - lunr
    - toc (puts a toc in the sidebar)
    - links (puts a link list page - must be content/widgetlinks)
- change the footer credits (i18n/en)
- SASS friendly CSS loading (baseof)
- multiple built in CSS files (baseof)
- less obnoxious read more (summary.html)
- shortcodes
    - teaser (put a page summary in place)
    - mini (like a tease, but puts the whole page content - has its own layout)


Known bugs / missing features:
- sections are just stuck at the beginning of a page list (and not counted in pagination)
- make an integrated css (using sass)

## Acknowledgement

This is based heavily on mainroad, including using some pieces as a base to hack on. 

To comply with the mainroad license, this theme is also released GPL.
