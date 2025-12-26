# 559Theme Code Critique and Improvement Plan

## Overview
The `559Theme` has evolved organically, leading to a mix of coding styles, duplicated logic, and tight coupling between Hugo templating and SASS styles. This makes maintenance difficult and increases the risk of regressions when changing styles.

## Key Issues

### 1. Fragmented CSS/SASS Architecture
*   **Issue**: `style.scss`, `v2-styles.css`, and `559.scss` are compiled and loaded independently.
*   **Consequence**: SASS variables and mixins cannot be shared between files. This leads to code duplication (e.g., color variables defined in multiple places).
*   **Consequence**: The browser has to make multiple requests (though HTTP/2 mitigates this, it's still not ideal for critical path CSS).

### 2. Heavy Use of Hugo Templating in SASS
*   **Issue**: Files like `style.scss` are full of `{{ if ... }}` and `{{ .Site.Params ... }}`.
*   **Consequence**: The files are not valid SASS. You cannot use standard SASS linters or tools.
*   **Consequence**: Logic is split between Hugo (server-side) and SASS (build-time), making it hard to reason about the final CSS.

### 3. "Old" vs "New" Theme Logic
*   **Issue**: Conditional logic for `themestyle` is scattered throughout the CSS files.
*   **Consequence**: This bloats the code and makes it hard to see what the active styles are.

### 4. `baseof.html` Complexity
*   **Issue**: The main template contains inline scripts, styles, and complex logic for loading resources.
*   **Consequence**: Hard to read and maintain. Inline styles/scripts are generally discouraged for Content Security Policy (CSP) reasons.

## Improvement Plan

### Phase 1: Unify SASS Compilation
**Goal**: Compile a single CSS file from a structured SASS hierarchy.

1.  **Create `_variables.scss` (as a template)**: A single file where Hugo parameters are injected into SASS variables.
    ```scss
    // assets/css/_hugo-variables.scss
    $highlight-color: {{ .Site.Params.style.vars.highlightColor | default "#e22d30" }};
    $theme-style: "{{ .Site.Params.themestyle | default "new" }}";
    ```
2.  **Refactor `style.scss` and `559.scss`**:
    *   Remove all `{{ ... }}` logic.
    *   Replace Hugo conditionals with SASS `@if $theme-style == "old" { ... }`.
    *   Rename to `_style.scss` and `_559.scss` (partials).
3.  **Create `main.scss`**:
    *   Import the generated variables.
    *   Import the partials.
    *   `@import "hugo-variables"; @import "style"; @import "559";`

### Phase 2: Clean up Templates
1.  **Extract Inline JS**: Move the "no-js" script and the "fullwidth" script into `assets/js/theme.js`.
2.  **Extract Inline CSS**: Move the "fullwidth" styles into `_utilities.scss` (imported by `main.scss`).
3.  **Simplify `baseof.html`**: It should just link to `main.css` and `theme.js`.

### Phase 3: Standardization
1.  **Naming Conventions**: Standardize on SASS variable names (kebab-case) vs Hugo params (camelCase).
2.  **Documentation**: Document the available parameters in `config.toml` clearly.

## Status Update (December 2025)

### Completed: Phase 1 (SASS Unification)
The SASS architecture has been successfully refactored to separate Hugo configuration from style logic.

*   **`assets/css/main.scss`**: Created as the single entry point. This file:
    *   Retrieves Hugo parameters (e.g., `.Site.Params.themestyle`).
    *   Maps them to SASS variables (e.g., `$theme-style`).
    *   Imports the style partials.
*   **`assets/css/_style.scss`**: Formerly `style.scss`.
    *   Converted to a pure SASS partial.
    *   All Hugo templating (`{{ ... }}`) has been removed.
    *   Logic now uses SASS `@if $theme-style == "old"` instead of Hugo `{{ if eq ... }}`.
*   **`assets/css/_559.scss`**: Formerly `559.scss`.
    *   Converted to a pure SASS partial.
    *   Cleaned of Hugo syntax.
*   **`layouts/_default/baseof.html`**: Updated to compile and link `main.scss` instead of individual files.

This change means the stylesheets are now valid SASS files that can be linted and edited with standard tools. The build process is cleaner and more robust.

## Modernization & Synchronization with Roadster

The `559Theme` is based on an older version of `mainroad` (now `roadster`). A comparison with the current `roadster` theme reveals several opportunities to modernize the template structure and reduce technical debt.

### 1. Modularize `baseof.html`
**Current State**: `559Theme/layouts/_default/baseof.html` is a monolithic file containing the entire `<head>` section, inline scripts, and complex logic.
**Roadster Approach**: `roadster` delegates almost all logic to partials:
*   `{{- partial "head.html" . -}}` handles the `<head>`.
*   `head.html` is further broken down into `head/seo.html`, `head/gfonts.html`, and `head/stylesheet.html`.

**Recommendation**:
*   Create `layouts/partials/head.html` and move the `<head>` content there.
*   Create `layouts/partials/head/css.html` to contain the SASS compilation logic we just built.
*   This will make `baseof.html` much easier to read and maintain.

### 2. Standardize Script Loading
**Current State**: `559Theme` has inline JavaScript in the `<head>` (e.g., the `no-js` class replacement).
**Roadster Approach**: `roadster` loads scripts at the end of the `<body>` tag and uses external files where possible.

**Recommendation**:
*   Move the inline `no-js` script to a partial or external file.
*   Adopt `roadster`'s pattern of loading non-critical scripts at the bottom of the page to improve performance.

### 3. Wrapper Structure & Full Width Mode
**Current State**: `559Theme` adds custom wrappers (`header-wrapper`, `sidebar-wrapper`, `footer-wrapper`) to `baseof.html`.
**Roadster Approach**: Uses a cleaner `container` > `wrapper` structure without these extra divs.

**Note**: An attempt to remove these wrappers caused layout regressions (footer appearing as sidebar). They have been retained for now to ensure stability. Future refactoring should investigate how to implement "Full Width Mode" without them, possibly by using more specific CSS selectors on the standard Roadster classes.

### 4. Visual Regressions & Fixes
*   **Subtitle Size**: The site subtitle was inadvertently shrunk to `10px` during the SASS refactor. This has been fixed by introducing a `$tagline-font-size` variable in `main.scss` (defaulting to `1rem`) and updating `_style.scss` to use it.

**Update**: We attempted to remove these wrappers to align with `roadster`, but this caused layout regressions (footer appearing as sidebar, sidebar stacking). The `559Theme` CSS (`_style.scss`) relies on these wrappers for flexbox layout and Full Width Mode targeting.
**Decision**: We have retained the wrappers in `baseof.html` to ensure stability. Future refactoring of `_style.scss` could allow their removal, but it is out of scope for the current cleanup.
