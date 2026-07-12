
{{/* include the CONTENT from another PAGE
   * (this requires things to be a findable page)
   *
   * adapted from https://discourse.gohugo.io/t/solved-remove-frontmatter-of-content-read-with-readfile/12682/10
 
    See also:
    https://discourse.gohugo.io/t/include-file-shortcode-for-including-files-with-shortcode-calls/16699

    but note this is an md shortcode (maybe it can be converted to an html shortcode using markdownify)

    when it comes time for headless resources, I might need
    https://discourse.gohugo.io/t/using-hugo-shortcodes-in-readfile/20161
    which talks about how to access resources from page bundles
 
   */}}
{{ $file := .Get 0 }}
{{ with .Site.GetPage $file }}
<h2><a href="{{.Permalink}}">{{.Title}}</a></h2>
{{.Summary}}
<details class="myexpand">
    <summary class="myexpand-head">Read more...</summary>
    {{ .Content }}
</details>
{{- else -}}
{{- errorf "Can't find page to put content from '%s'" (.Get 0) -}}
{{end}}