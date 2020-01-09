{{ range .Site.Pages }}
+ [{{ .Title }}]({{ .RelPermalink }})
{{ end }}