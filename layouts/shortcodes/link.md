{{- /* Mike's first attempt to make a Hugo Template
     * the first param is the page
     * the second param (optional) is the anchor

     this is less helpful when you want to change the text of the link,
     but that case is well handled with just using raw Hugo
     */ -}}
{{- $pagename := .Get 0 -}}
{{- $anchorname := .Get 1 -}}
{{- $target := relref . $pagename -}}
[{{- with .Site.GetPage $pagename -}}{{- .Title -}}{{end}}{{- with $anchorname -}} &nbsp; ({{- $anchorname -}}){{- end -}}]({{ $target }}{{- with $anchorname -}}#{{- anchorize $anchorname -}}{{- end -}})