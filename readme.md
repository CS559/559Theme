# CS559 Theme

A theme created by Michael Gleicher to make a class web page.

This builds on the "MainRoad" theme - it needs to be "mixed in" to that theme.in the config.toml file, have the line

~~~toml
theme = ["559Theme","mainroad"]
~~~

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
- less obnoxious read more (summary.html) (set myreadmore to true)
- shortcodes
    - teaser (put a page summary in place)
    - mini (like a tease, but puts the whole page content - has its own layout)

Known bugs / missing features:
- sections are just stuck at the beginning of a page list (and not counted in pagination)
    - but note that sections ARE INCLUDED in a pagelist (different than default mainroad)
- make an integrated css (using sass)
- mathjax should include the cool hack that allows us to quote math (see the workbook theme)
- the new mainroad includes better logo support - revisit how header.html works

## startup process

- hugo new site 
- git init
- git submodule add git@github.com:Vimux/Mainroad.git themes/mainroad
- git submodule add git@github.com:CS559/559Theme.git themes/559Theme
- git submodule init
- git submodule update
- create a config.toml

- create a content/widgetlinks.md  - width headless:true
### things for the config.toml file

Use both themes: look in 559Theme first
~~~toml
theme = ["559Theme","mainroad"]
~~~

Generate multiple outputs so we can use Lunr:
~~~
[outputs]
home = [ "HTML", "RSS", "JSON"]
~~~

This is important so that we render HTML in the markdown:
~~~
[markup.goldmark.renderer]
unsafe= true
~~~

## Acknowledgement

This is based heavily on mainroad, including using some pieces as a base to hack on. 

To comply with the mainroad license, this theme is also released GPL.
