# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['goodwiki']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.6,<9.0.0',
 'httpx>=0.24.1,<0.25.0',
 'multiprocess>=0.70.15,<0.71.0',
 'mwparserfromhell>=0.6.4,<0.7.0',
 'pyarrow>=12.0.1,<13.0.0',
 'pypandoc>=1.11,<2.0',
 'tqdm>=4.66.1,<5.0.0',
 'wikipedia-api>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'goodwiki',
    'version': '1.0.0',
    'description': 'Utility that converts Wikipedia pages into GitHub-flavored Markdown.',
    'long_description': '# GoodWiki\n\nGoodWiki is a Python package that carefully converts Wikipedia pages into GitHub-flavored Markdown. Converted pages preserve layout features like lists, code blocks, math, and block quotes.\n\nThis package is used to generate the [GoodWiki Dataset](https://github.com/euirim/goodwiki).\n\n## Installation\n\nThis package supports Python 3.11+.\n\n1. Install via pip.\n\n```bash\npip install goodwiki\n```\n\n2. Install pandoc. Follow instructions [here](https://pandoc.org/installing.html).\n\n## Usage\n\n### Initializing Client\n\n```python\nimport asyncio\nfrom goodwiki import GoodwikiClient\n\nclient = GoodwikiClient()\n```\n\nYou can also optionally provide your own user agent (default is `goodwiki/1.0 (https://euirim.org)`):\n\n```python\n\nclient = GoodwikiClient("goodwiki/1.0 (bob@gmail.com)")\n```\n\n### Getting Single Page\n\n```python\npage = asyncio.run(client.get_page("Usain Bolt"))\n```\n\nYou can also optionally include styling syntax like bolding to the final markdown:\n\n```python\npage = asyncio.run(client.get_page("Usain Bolt", with_styling=True))\n```\n\nYou can access the resulting data via properties. For example:\n\n```python\nprint(page.markdown)\n```\n\n### Getting Category Pages\n\nTo get a list of page titles associated with a Wikipedia category, run the following:\n\n```python\nclient.get_category_pages("Category:Good_articles")\n```\n\n### Converting Existing Raw Wikitext\n\nIf you\'ve already downloaded raw wikitext from Wikipedia, you can convert it to Markdown by running:\n\n```python\nclient.get_page_from_wikitext(\n\traw_wikitext="RAW_WIKITEXT",\n\t# The rest of the fields are meant for populating the final WikiPage object\n\ttitle="Usain Bolt",\n\tpageid=123,\n\trevid=123,\n)\n```\n\n## Methodology\n\nFull details are available in this package\'s [GitHub repo README](https://github.com/euirim/goodwiki).\n\n## External Links\n\n* [GitHub](https://github.com/euirim/goodwiki)\n* [Dataset](https://huggingface.co/datasets/euirim/goodwiki)\n',
    'author': 'Euirim Choi',
    'author_email': 'euirim@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/euirim/goodwiki',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
