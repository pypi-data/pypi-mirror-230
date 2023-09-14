# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poi', 'poi.visitors']

package_data = \
{'': ['*']}

install_requires = \
['xlsxwriter>=1.1,<2.0']

setup_kwargs = {
    'name': 'poi',
    'version': '1.1.2',
    'description': 'Write Excel XLSX declaratively.',
    'long_description': '# Poi: The Declarative Way to Excel at Excel in Python\n\n![CI](https://github.com/ryanwang520/poi/actions/workflows/tests.yaml/badge.svg)\n\n## Why Poi?\n\nCreating Excel files programmatically has always been a chore. Current libraries offer limited flexibility, especially when you need more than a basic table. That\'s where Poi comes in, offering you a simple, intuitive, yet powerful DSL to make Excel files exactly the way you want them.\n\n\n\n## Installation\n\n```bash\npip install poi\n```\n\n## Quick start\n\n### Create a sheet object and write to a file.\n\n```python\nfrom poi import Sheet, Cell\nsheet = Sheet(\n    root=Cell("hello world")\n)\n\nsheet.write(\'hello.xlsx\')\n```\n\n![hello](https://github.com/baoshishu/poi/raw/master/docs/assets/hello.png)\n\nSee, it\'s pretty simple and clear.\n\n\n### Create a Dynamic Table with Conditional Formatting\n\n\n```python\nfrom typing import NamedTuple\nfrom datetime import datetime\nimport random\n\nfrom poi import Sheet, Table\n\n\nclass Product(NamedTuple):\n    name: str\n    desc: str\n    price: int\n    created_at: datetime\n    img: str\n\n\ndata = [\n    Product(\n        name=f"prod {i}",\n        desc=f"desc {i}",\n        price=random.randint(1, 100),\n        created_at=datetime.now(),\n        img="./docs/assets/product.jpg",\n    )\n    for i in range(5)\n]\ncolumns = [\n    {\n        "type": "image",\n        "attr": "img",\n        "title": "Product Image",\n        "options": {"x_scale": 0.27, "y_scale": 0.25},\n    },\n    ("name", "Name"),\n    ("desc", "Description"),\n    ("price", "Price"),\n    ("created_at", "Create Time"),\n]\nsheet = Sheet(\n    root=Table(\n        data=data,\n        columns=columns,\n        row_height=80,\n        cell_style={\n            "color: red": lambda record, col: col.attr == "price" and record.price > 50\n        },\n        date_format="yyyy-mm-dd",\n        align="center",\n        border=1,\n    )\n)\nsheet.write("table.xlsx")\n```\n\n\n![table](https://github.com/baoshishu/poi/raw/master/docs/assets/table.png)\n\nSee how simple it is to create complex tables? You just wrote a dynamic Excel table with conditional formatting a few lines of code!\n\n\n### Features\n\n* 🎉 Declarative: Create Excel files with a simple, intuitive DSL.\n* 🔥 Fast: Export large Excel files in seconds.\n* 🚀 Flexible Layouts: Create any layout you can imagine with our intuitive Row and Col primitives.\n\n\n### Documentation\n\nFor more details, check our comprehensive [Documentation](https://ryanwang520.github.io/poi/)\n',
    'author': 'Ryan Wang',
    'author_email': 'hwwangwang@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/baoshishu/poi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
