{{/* Places a page inline inside of another page
   * note that it must be a page (and not just a markdown fragment)
   * it is processed with the "inline" template
   */}}
{{- $page := .Site.GetPage (.Get 0) -}}
{{- with $page -}}
<div class="inline">
{{ .Render "inline" }}
</div>
{{- else -}}
** ERROR! **
{{- end -}}
