{{- $page := .Site.GetPage (.Get 0) -}}
{{- with $page -}}
<div class="teaser">
{{ .Render "mini" }}
</div>
{{- end -}}
