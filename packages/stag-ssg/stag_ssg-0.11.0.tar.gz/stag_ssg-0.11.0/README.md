<p align="center">
  <a href="https://git.goral.net.pl/stag">
    <img alt="Logo featuring a stag" src="https://git.goral.net.pl/stag.git/plain/doc/stag.png" width="320"/>
  </a>
</p>

# Stag

Stag is a simple, extensible static site generator, where almost every part
is a plug in. It's almost too easy to extend it with your own
functionalities.

[Online documentation](https://pages.goral.net.pl/stag)

# Features

Out of the box Stag comes with the following features:

- pages can be generated from Markdown with enabled support for footnotes,
  fenced code blocks and some typographic goodies.
- support for Asciidoc (via asciidoctor)
- generic support for file front matters
- Jinja2 templates
- taxonomies (e.g. tags)
- RSS feeds
- generation of nice URLs:
  - _foo/index.md_ → _foo/index.html_
  - _bar.md_ → _bar/index.html_
- extensible with plugins and macros (shortcodes)

# Installation

PyPI: https://pypi.org/project/stag-ssg/
