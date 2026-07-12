{{- /* Mike's first attempt to make a Hugo Template
     * the first param is the page
     * the second param (optional) is the anchor
     *
     * this is effectively the "link" shortcode except that it puts
     * /pages in the name - this shortcode should be depricated
     */ -}}
{{- $pagename := (printf "/pages/%s" (.Get 0)) -}}
{{- $anchorname := .Get 1 -}}
{{- $target := relref . $pagename -}}
[{{- with .Site.GetPage $pagename -}}{{- .Title -}}{{end}}{{- with $anchorname -}} &nbsp; ({{- $anchorname -}}){{- end -}}]({{ $target }}{{- with $anchorname -}}#{{- anchorize $anchorname -}}{{- end -}})