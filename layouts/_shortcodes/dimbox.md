{{- /*
  dimbox — wrap inner content in <div class="dimbox"> (a dimmed callout box).
  usage: {{% dimbox %}}note text{{% /dimbox %}}
  params: none; takes inner (markdown) content.
*/ -}}
<div class="dimbox">
{{ .Inner }}
</div>{{ "<!-- end dimbox -->" | safeHTML }}