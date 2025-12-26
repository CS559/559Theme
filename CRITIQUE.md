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
