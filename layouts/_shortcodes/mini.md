{{- /*
  mini — embed another page rendered with its "mini" view, inside a teaser box.
  usage: {{% mini "/path/to/page" %}}
  params: 0 = logical page path. (cf. teaser = "summary" view; inline = full content.)
*/ -}}
{{- $page := .Site.GetPage (.Get 0) -}}
{{- with $page -}}
<div class="teaser">
{{ .Render "mini" }}
</div>
{{- end -}}
