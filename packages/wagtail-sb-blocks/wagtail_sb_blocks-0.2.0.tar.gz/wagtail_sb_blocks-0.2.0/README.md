![Community-Project](https://gitlab.com/softbutterfly/open-source/open-source-office/-/raw/master/banners/softbutterfly-open-source--banner--community-project.png)

![PyPI - Supported versions](https://img.shields.io/pypi/pyversions/wagtail-sb-blocks)
![PyPI - Package version](https://img.shields.io/pypi/v/wagtail-sb-blocks)
![PyPI - Downloads](https://img.shields.io/pypi/dm/wagtail-sb-blocks)
![PyPI - MIT License](https://img.shields.io/pypi/l/wagtail-sb-blocks)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a7111b162e8749cab6d58f8b8724bac0)](https://app.codacy.com/gl/softbutterfly/wagtail-sb-blocks/dashboard?utm_source=gl&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/a7111b162e8749cab6d58f8b8724bac0)](https://app.codacy.com/gl/softbutterfly/wagtail-sb-blocks/dashboard?utm_source=gl&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)
[![pipeline status](https://gitlab.com/softbutterfly/open-source/wagtail-sb-blocks/badges/master/pipeline.svg)](https://gitlab.com/softbutterfly/open-source/wagtail-sb-blocks/-/commits/master)

# Wagtail Blocks

Package with basic, adaptable and reusable blocks to build awesome sites with wagtail.

## Requirements

- Python 3.8.1 or higher
- Wagtail 3.0 or higher
- Django 3.2 or higher

## Install

```bash
pip install wagtail-sb-blocks
```

## Usage

Add `wagtail_sb_blocks` to your `INSTALLED_APPS` settings

```python
INSTALLED_APPS = [
  # ...
  "wagtail_sb_blocks",
  # ...
]
```

In your stream blocks use blocks from this package to rapid development.

```python
from wagtail.blocks import StreamBlock

from wagtail_sb_blocks.blocks import TitleBlock, ParagraphBlock, FigureBlock, ButtonBlock

class EnhancedHTMLBlock(StreamBlock):
    title = TitleBlock()
    paragraph = ParagraphBlock()
    figure = FigureBlock()
    button = ButtonBlock()
```

## Docs

- [Ejemplos](https://gitlab.com/softbutterfly/open-source/wagtail-sb-blocks/-/wikis)
- [Wiki](https://gitlab.com/softbutterfly/open-source/wagtail-sb-blocks/-/wikis)

## Changelog

All changes to versions of this library are listed in the [change history](CHANGELOG.md).

## Development

Check out our [contribution guide](CONTRIBUTING.md).

## Contributors

See the list of contributors [here](https://gitlab.com/softbutterfly/open-source/wagtail-sb-blocks/-/graphs/develop).
