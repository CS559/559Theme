{{- /*
  teaser — embed another page's "summary" view inside <div class="teaser">.
  usage: {{% teaser "/path/to/page" %}}
  params: 0 = logical page path. (cf. teasehtml = unwrapped; mini = the "mini" view.)
*/ -}}
{{- $page := .Site.GetPage (.Get 0) -}}
{{- with $page -}}
<div class="teaser">
{{ .Render "summary" }}
</div>
{{- end -}}
