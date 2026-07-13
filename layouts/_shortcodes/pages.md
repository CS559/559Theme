{{- /*
  pages — DEAD tombstone: errorf's on ANY use. Superseded by `link` (or `page`).
  @dead-weight: kept as a tripwire pointing authors to the replacement; left as
    errorf (not warnf) on purpose. Original impl parked in deprecated/pages.md.
*/ -}}
{{ errorf "The pages shortcode has been deprecated - use link instead (or did you mean page?) [looking for `%s']" (.Get 0) }}