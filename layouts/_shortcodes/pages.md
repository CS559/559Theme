{{/* @dead-weight: tombstone — errorf's on any use to force migration to `link`
     (or `page`). Kept intentionally as a tripwire; reconsider full removal once
     no consumer could still reference it. Left as errorf (not warnf) on purpose.
     The original implementation is parked in deprecated/pages.md. */}}
{{ errorf "The pages shortcode has been deprecated - use link instead (or did you mean page?) [looking for `%s']" (.Get 0) }}