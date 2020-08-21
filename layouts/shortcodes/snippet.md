{{/* inserts a markdown snippet from assets 
   * requires the asset to be a plain markdown (not a page with frontmatter)
   * naively looks in /assets/snippets
   */}}
{{- $name := .Get 0 }}
{{- $fullname := (printf "/assets/snippets/%s" $name) -}}
{{- $fullname | readFile -}}