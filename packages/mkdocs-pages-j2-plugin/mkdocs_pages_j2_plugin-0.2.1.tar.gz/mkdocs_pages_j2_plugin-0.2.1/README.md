# mkdocs-pages-j2-plugin

This plugin builds `.pages` files from `.pages.j2` files, using Jinja2 to render the templates.
This plugin is particularly useful when used together with the
[mkdocs-awesome-pages-plugin](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin).

## Installation

Install the package with pip:

```bash
pip install mkdocs-pages-j2-plugin
```

Activate the plugin in `mkdocs.yml`:

```yaml
plugins:
  - search
  - pages-j2
  - awesome-pages
```

## Usage

Example of a `.pages.j2` file:

```jinja2
title: Page Title
nav:
    - Welcome: index.md
{%- for i in range(1,3) %}
    - My Page {{ i }}: p{{ i }}.md
{%- endfor %}
```

The plugin will render the _Jinja2_ template above and create a `.pages` file with the following content:

```text
title: Page Title
nav:
    - Welcome: index.md
    - My Page 1: p1.md
    - My Page 2: p2.md
```
