# CS559 Theme

A theme created by Michael Gleicher to make a class web page.

This builds on the "MainRoad" theme - it needs to be "mixed in" to that theme.in the config.toml file, have the line
````toml
theme = ["559Theme","mainroad"]
````
and make sure that both mainroad and 559Theme are in the themes directory

- New variables for tuning:
    - noheader - set to true on a page to skip the header (default/baseof.html)

## Acknowledgement

This is based heavily on mainroad, including using some pieces as a base to hack on. 

To comply with the mainroad license, this theme is also released GPL.
