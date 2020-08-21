{{/* include the CONTENT from another PAGE
   * (this requires things to be a findable page)
   *
   * adapted from https://discourse.gohugo.io/t/solved-remove-frontmatter-of-content-read-with-readfile/12682/10
   */}}
{{ $file := .Get 0 }}
{{ with .Site.GetPage $file }}{{.Content}}{{end}}