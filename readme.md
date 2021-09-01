# CS559 Theme

A theme created by Michael Gleicher to make a class web page. Over time, it evolved to also do my home page, so there is a lot of stuff specific to that.

This builds on the "MainRoad" theme - it needs to be "mixed in" to that theme.in the config.toml file, have the line

~~~toml
theme = ["559Theme","mainroad"]
~~~

and make sure that both mainroad and 559Theme are in the themes directory

- New variables for tuning:
  - noheader - set to true on a page to skip the header (default/baseof.html) - this was meant to allow the home page to look different
  - myreadmore - true (by default) for a less obnoxious read me in a summary (and a link if the summary is the whole page)

Changes (not exhaustive):

- Add Section summaries to page list summaries (default/list.html)
- Add lunr search (content/lunr-search, widgets/lunr, index.json)
- A taglist for post_meta
- Put the logo in the header (assets/svg, partials/header)
- New widgets
  - lunr (search box - sends things to the lunr page where the work happens)
  - toc (puts a toc in the sidebar)
  - links (puts a link list page - must be content/widgetlinks - be sure to create **widgetlinks**)
  - allpages (makes a list of all pages in a site - not sure how to scope it correctly, probably not that valuable)
  - archive (puts a message that this is an archived class - be sure to set Site.Params.Archive and Site.Params.Archivenote)
  - recents (useful thing from other blog-like themes)
  - toc (puts the toc in a widget - which can be a useful place for it)
  - important - makes a list of important pages (uses a site parameter "ImportantPages")
  - thisweek - puts a "this week" page in the sidebar
- change the footer credits (i18n/en)
- SASS friendly CSS loading (baseof)
- multiple built in CSS files (baseof)
- less obnoxious read more (summary.html) (set myreadmore to true)
- shortcodes (*note that mainroad doesn't provide any!*)
  - allpages (makes a list of all pages)
  - anchorlink
  - assetlink
  - bold-red (makes a span with a `boldred` class)
  - comment (comments out something)
  - content (includes the content of another page inline)
  - content (inserts the content of another page)
  - dimbox (makes a dimbox div)
  - expand (puts text into an expander)
  - figure (improved on the Hugo figure to allow for rsrc parameters)
  - htmllink (shows the HTML of a reference - gives the whole link)
  - includemd (includes a markdown file - which is not a page)
  - inline (includes another page in place - uses a special style template)
  - leftpic (puts a picture to the left of text)
  - link (makes a relref link - and gets the page title)
  - linkit (probably could be deprecated)
  - listtoc (makes a table of contents for a list page)
  - listtoc (puts a table of contents in place in a document, rather than at the top)
  - mailto
  - mini (like a tease, but puts the whole page content - has its own layout)
  - pages (like link, but goes into pages)
  - resource-image.md (put a page resource image into markdown)
  - resource-link.md (makes a link to a page resource)
  - resource-svg (puts an SVG file in place - allows for showing the code)
  - snippet.md (include a markdown snippet from assets/snippets.md)
  - static (generates a link to a static object)
  - tableofcontents (does the regular table of contents, inline)
  - teasehtml
  - teaser (put a page summary in place)
  - url (makes a link to a URL with the URL as the text)
- pagination of sections is improved
  - pagination controls has first/last
  - section pages can control paginate and top_pagination (this is per section)
    - but there is a site default (for top_pagination)
  - lists show subsections, not just pages (hacky right now)
- switch the "expand" shortcode to use HTML details (see book)
- footer uses lastmod (good with git - *be sure to turn on git*)
- header hard codes wisc styling and logo
- sections for talks and videos (and other collection of objects)
  - some attempts for unification
  - put "visual_summary" as a page parameter (to true) to get it
- the header (logo.html) is different than mainroad - to get the spacing right (vertical alignment)
- some colors and stylings are changed in styles.css - done since styles.css got converted to scss

### New Section Variables

- visual_summary - uses a format for talks/videos where everything has a place for a thumbnail and links to the various assets are shown

### New Page Variables

- resourcethumb - allows you to give a thumbnail that is a page resource/ this is resized (based on videosize)

## Using Links

The **link** short code makes a link to a page - looking the page up and getting its title. The (optional) second parameter is the *anchor* on the page. If you want to give a page title (rather than looking it up), it is better to just use the regular markdown notation.

Link uses `.Site.GetPage` to find the page - so the string parameter is the "page name" the file name *should* work. But, often it will say that things are ambiguous if the path isn't in the same directory. It never hurts to give a full path "/foo/bar" (with the leading slash). This confuses me all the time. I have no idea why sometimes it works, and other times it does not.

One thing to beware of (it drives me nuts): if a tag or category has the same name as a page, there can be the potential for name ambiguities. Beware.

## New UW Theme Based Design

- change between old and new by using themestyle = "new" or "old" in config.toml
- update miscellaneous parameters to the website such as color, headers, backgrounds, using config.toml in the 559Theme directory
- config.toml theme parameters:
  - highlightColor: color that lights up on hovers and other miscellaneous places on website
  - uwred: basic dark red color for UW
  - fontSans: sans font used in secondaryFontFamily, used in headings and sidebar
  - fontMono: font used in primaryFontFamily, used for body text
  - bodyFontSize: size of body text
  - containerWidth: width of container for website
  - headerColor: color for headers
  - figColor: color of figure caption text
  - codeBackground: color of background on code
  - codeBorder: style of border around code
  - codeColor: text color for pre
  - logoColor: color of logo text
  - taglineColor: color of tagline text
  - menuListColor: background color of menu and submenu
  - hoverTextColor: color of menu text upon hover
  - submenuBorderTop: color for border on top of submenu
  - tocSubheadingColor: color for table of contents subheading
  - authorboxBorder: styling for authorbox border
  - nextBtnColor: text color for next pagination button
  - nextBtnBack: background color for next pagination button
  - paginItemColor: text color for pagination items
  - paginItemBack: background color for pagination items
  - sidebarLinkUnderline: toggle between having underline when hovering on sidebar items for the "old" style
  
## Known bugs / missing features

- it might be better to make this separate / different from my home page, since they have different uses/needs
- pagination is set per page, but top_paginate is global
- I don't know why the section thing works now (the way mainroad does it does not seem different)
- make an integrated css (using sass)
- mathjax should include the cool hack that allows us to quote math (see the workbook theme)
- the new mainroad includes better logo support - revisit how header.html works
- mainroad doesn't seem to work if the root page is `index.md` - it has to be `_index.md`
  - workaround: use `_index.md` but make the `mainSections` in config.toml not have any posts
- lunr search doesn't check page titles (which would be really useful) - although the code seems to say that it does
- this is still heavily dependent on mainroad - it would be nice to remove that dependence
- paginator could use better icons
- menu active tabs seems to not completely work
- base URLs are still required for the search to work

## startup process

- hugo new site
- git init
- git submodule add git@github.com:Vimux/Mainroad.git themes/mainroad
- git submodule add git@github.com:CS559/559Theme.git themes/559Theme
- git submodule init
- git submodule update
- create a config.toml
- create a content/widgetlinks.md  - width headless:true

These GIT incantations help keep the subrepos on track if you care about that:

- git submodule foreach --recursive git checkout master

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

You do need to either set `baseURL` or use `hugo --baseURL` even if everything uses relative paths, as the `index.json` (used for text search) does not

## for the talks and videos

In general, assets get linked automatically if they are page resources.

However: you might want to put assets in an external directory. Use the `extpdfs` (or similar) page properties to give the link.

- the the link doesn't have "http" in it, it is assumed that it is in the assetStore link (directory) from Site.Params

## Acknowledgement

This is based heavily on mainroad, including using some pieces as a base to hack on.

To comply with the mainroad license, this theme is also released GPL.
