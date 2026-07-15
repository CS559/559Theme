# Known to-dos for the 559 Theme

1. ~~Update to the new mathematics implementation~~ — done: `math`/`displaymath`
   now render via Hugo's native `transform.ToMath` (KaTeX) at build time, no
   client-side JS. See `docs/math.md`.
2. try out better permalink structure for tags/taxonomies
    - this seemed to come around 1.115 and 1.118