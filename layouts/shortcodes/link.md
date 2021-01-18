{{- /* Mike's first attempt to make a Hugo Template
     * the first param is the page
     * the second param (optional) is the anchor

     this is less helpful when you want to change the text of the link,
     but that case is well handled with just using raw Hugo

    new:
[{{- $pagetitle -}} &nbsp ({{- $anchorname -}})]({{- $target-}}#{{- anchorize $anchorname -}})

     old page title:
     {{- with .Site.GetPage $pagename -}}{{- .Title -}}{{end}}{{- with $anchorname -}} &nbsp; ( {{- $anchorname -}}){{- end -}}
     */ -}}
{{- $pagename := .Get 0 -}}
{{- $pagetitle := (.Site.GetPage $pagename).Title -}}
{{- $anchorname := .Get 1 -}}
{{- $target := relref . $pagename -}}
{{/** too messy to deal with the different cases - so split**/}}
{{- with $anchorname -}}{{/* if there is an anchor */}}
[{{- $pagetitle -}}&nbsp;({{- $anchorname -}})]({{- $target -}}#{{- anchorize $anchorname -}})
{{- else -}}{{/* there is no anchor */}}
[{{- $pagetitle -}}]({{- $target -}})
{{- end -}}