{{- /* Mike's first attempt to make a Hugo Template
     * the first param is the page
     * the second param (optional) is the anchor
     */ -}}
{{- $pagename := .Get 0 -}}
{{- $anchorname := .Get 1 -}}
{{- $target := relref . $pagename -}}
[{{ with .Site.GetPage $pagename}}{{- .Title -}}{{end}}]({{ $target }}{{ with $anchorname }}#{{ $anchorname }}{{end}})