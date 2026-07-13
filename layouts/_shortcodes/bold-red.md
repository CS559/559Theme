{{- /*
  bold-red — wrap inner text in <span class="boldred"> (bold-red emphasis).
  usage: {{% bold-red %}}important{{% /bold-red %}}
  params: none; takes inner content.
*/ -}}
<span class="boldred">{{ .Inner }}</span>