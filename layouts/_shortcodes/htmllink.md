{{- /*
  htmllink — show an internal page's absolute URL as the visible, clickable link text.
  usage: {{% htmllink "some/page" %}}   ->   [https://…/some/page/](https://…/some/page/)
  params: 0 = logical page path (resolved with `ref`). (cf. link = uses the page title as the text.)
*/ -}}
{{- $ref := ref . (.Get 0) -}}
[{{- $ref -}}]({{$ref}})
