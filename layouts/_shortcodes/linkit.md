{{- /*
  linkit — make an arbitrary URL clickable, using the URL itself as the link text.
  usage: {{% linkit "https://example.com/x" %}}   ->   [https://example.com/x](https://example.com/x)
  params: 0 = URL, used verbatim as both text and href. For external URLs; does no page lookup.
*/ -}}
[{{- .Get 0 -}}]({{- .Get 0 -}})