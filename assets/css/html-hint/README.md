## Gleicher's Version of HTML Hint

This began with HTML Hint - but then Mike Gleicher modernized it.

HTML hint didn't change (much) - I just made it "compile" with a more modern environment.

1. The example (which was written in React) used some archaic build system - so npm couldn't even fetch the dependencies. So I ditched the example and npm (since the build process is just running sass).
2. The code was sass (indent form) - so I used an online tool to convert it to scss. This required some manual fixes as well. And for good measure, I fixed the things that caused deprecation warnings (mainly divisions)
3. The code used an old (2.2) version of hint.css - I downloaded the new hint.css, but even that isn't compatible with the version of sass I have. Some manual fixes were required.
4. I made a new example that is much simpler - straight hand-written html. 
5. There is a weirdness that the "unstyled" (no coloring) hints,css does give a black arrow, whereas the hmtl-hints does not. I wasn't able to figure this out. So I added a test case in himl-hint.scss.
6. I was not able to figure out how to get the pointer to change

## HTML HINT

*based on [hint.css](https://github.com/chinchang/hint.css) with html content support*

The main disadvantage of [hint.css](https://github.com/chinchang/hint.css) is it's inability to show html content inside hint.
This css library extends [hint.css](https://github.com/chinchang/hint.css) with html hints.

#### Example

[Base, click to view](http://istarkov.github.io/html-hint/#exampleMain)

### Install

```bash
npm install --save html-hint
```

### Usage

```html
<div class="hint--html hint--top">
  Place here any element
  <div class="hint__content">
    Place here your tooltip HTML content
  <div>
</div>
```

If you are prefer to use css-modules you can use composes

```html
<div class={styles.myClass}>
  Place here any element
  <div class={styles.myTooltip}>
    Place here your tooltip HTML content
  <div>
</div>
```

```scss
@import 'html-hint'

.myClass
  composes: hint--html
  composes: hint--top
  composes: hint--info
  cursor: pointer

.myTooltip
  composes: hint__content
```

There are different placement options
- `hint--top-left`, `hint--top`, `hint--top-right`;
- `hint--left`, `hint--right`,
- `hint--bottom-left`, `hint--bottom`, `hint--bottom-right`,

And different type options
- `hint--warning`, `hint--error`, `hint--info`, `hint--success`

(_To change color you can also use mixin_)

```scss
.myClass
  composes: hint--html
  composes: hint--top
  @include hint-color(yellow)
  cursor: pointer
```

#### Placement options example

[Base, click to view](http://istarkov.github.io/html-hint/#exampleMain)

---

By default tootips are not hoverable, adding `hint--hoverable` class makes them hoverable.

```html
<div class="hint--html hint--top hint--hoverable">
  Place here any element
  <div class="hint__content">
    Place here your tooltip HTML content
  <div>
</div>
```

#### Hoverable example

[Hoverable example, click to view](http://istarkov.github.io/html-hint/#exampleHoverable)

Sometimes you need to set hover by yourself.

Using `hint--always` class you will make tooltip always visible,
using `hint--hidden` you will prevent tooltip to show.

(_both hint--always and hint--hidden will hide tooltip on hover_)

#### hint--always example

[Always example, click to view](http://istarkov.github.io/html-hint/#exampleAlways)

### Contribute

```bash
npm install
npm run start
# open http://localhost:4000 and you will get hot reloadable env
```

### License

MIT (http://www.opensource.org/licenses/mit-license.php)
