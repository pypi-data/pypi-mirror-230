# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oc_ocdm',
 'oc_ocdm.counter_handler',
 'oc_ocdm.graph',
 'oc_ocdm.graph.entities',
 'oc_ocdm.graph.entities.bibliographic',
 'oc_ocdm.metadata',
 'oc_ocdm.metadata.entities',
 'oc_ocdm.prov',
 'oc_ocdm.prov.entities',
 'oc_ocdm.resources',
 'oc_ocdm.support',
 'oc_ocdm.test',
 'oc_ocdm.test.counter_handler',
 'oc_ocdm.test.graph',
 'oc_ocdm.test.graph.entities',
 'oc_ocdm.test.graph.entities.bibliographic',
 'oc_ocdm.test.metadata',
 'oc_ocdm.test.metadata.entities',
 'oc_ocdm.test.prov',
 'oc_ocdm.test.prov.entities',
 'oc_ocdm.test.reader',
 'oc_ocdm.test.resources',
 'oc_ocdm.test.storer',
 'oc_ocdm.test.support']

package_data = \
{'': ['*'], 'oc_ocdm.test': ['coverage/*']}

install_requires = \
['SPARQLWrapper==2.0.0',
 'filelock>=3.6.0,<4.0.0',
 'pyshacl==0.23.0',
 'rdflib>=6.0.0,<7.0.0']

entry_points = \
{'console_scripts': ['test = scripts:main']}

setup_kwargs = {
    'name': 'oc-ocdm',
    'version': '7.3.1',
    'description': 'Object mapping library for manipulating RDF graphs that are compliant with the OpenCitations datamodel.',
    'long_description': '# oc_ocdm\n[<img src="https://img.shields.io/badge/powered%20by-OpenCitations-%239931FC?labelColor=2D22DE" />](http://opencitations.net)\n[![Run tests](https://github.com/opencitations/oc_ocdm/actions/workflows/run_tests.yml/badge.svg)](https://github.com/opencitations/oc_ocdm/actions/workflows/run_tests.yml)\n![Coverage](https://raw.githubusercontent.com/opencitations/oc_ocdm/master/oc_ocdm/test/coverage/coverage.svg)\n[![Documentation Status](https://readthedocs.org/projects/oc-ocdm/badge/?version=latest)](https://oc-ocdm.readthedocs.io/en/latest/?badge=latest)\n[![PyPI version](https://badge.fury.io/py/oc-ocdm.svg)](https://badge.fury.io/py/oc-ocdm)\n![PyPI](https://img.shields.io/pypi/pyversions/oc_meta)\n\n[![DOI](https://zenodo.org/badge/322327342.svg)](https://zenodo.org/badge/latestdoi/322327342)\n[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)\n\nDocumentation can be found here: [https://oc-ocdm.readthedocs.io](https://oc-ocdm.readthedocs.io).\n\n**oc_ocdm** is a Python &ge;3.7 library that enables the user to import, produce, modify and export RDF data\nstructures which are compliant with the [OCDM v2.0.1](https://figshare.com/articles/Metadata_for_the_OpenCitations_Corpus/3443876) specification.\n\n## User\'s guide\nThis package can be simply installed with **pip**:\n``` bash\n    pip install oc_ocdm\n```\n**Please, have a look at the notebooks [available here](https://github.com/opencitations/oc_ocdm/blob/master/notebooks/).**\n\n## Developer\'s guide\n\n### First steps\n  1. Install Poetry:\n``` bash\n    pip install poetry\n```\n  2. Clone this repository:\n``` bash\n    git clone https://github.com/iosonopersia/oc_ocdm\n    cd ./oc_ocdm\n```\n  3. Install all the dependencies:\n``` bash\n    poetry install\n```\n  4. Build the package (_output dir:_ `dist`):\n``` bash\n    poetry build\n```\n  5. Globally install the package (_alternatively, you can also install it inside a virtual-env,\n  by providing the full path to the .tar.gz archive_):\n``` bash\n    pip install ./dist/oc_ocdm-<VERSION>.tar.gz\n```\n  6. If everything went the right way, than you should be able to use the `oc_ocdm` library in your Python modules as follows:\n``` python\n    from oc_ocdm.graph import GraphSet\n    from oc_ocdm.graph.entities.bibliographic import AgentRole\n    # ...\n```\n\n### How to run the tests\nJust run the following command inside the root project folder:\n``` bash\n    poetry run test\n```\n\n### How to manage the project using Poetry\nSee [Poetry commands documentation](https://python-poetry.org/docs/cli/).\n\n**AAA: when adding a non-dev dependency via `poetry add`, always remember to add\nthat same dependency to the `autodoc_mock_imports` list in `docs/source/conf.py`**\n(otherwise "Read the Docs" won\'t be able to compile the documentation correctly!).\n\n### How to publish the package onto Pypi\n``` bash\n    poetry publish --build\n```\n### Install dependencies needed for the documentation\n``` bash\n    pip install Sphinx sphinx_rtd_theme\n```\n### How to generate the documentation\n``` bash\n    rm ./docs/source/modules/*\n    sphinx-apidoc  -o ./docs/source/modules oc_ocdm *test*\n```\n\n### How to build the documentation\n___\n**Warning! In order to avoid getting the following `WARNING: html_static_path entry \'_static\' does not exist`, you\'ll\nneed to manually create an empty `_static` folder with the command:**\n``` bash\n    mkdir docs/source/_static\n```\n___\n  1. Always remember to move inside the `docs` folder:\n``` bash\n    cd docs\n```\n  2. Use the Makefile provided to build the docs:\n      + _on Windows_\n        ```\n            make.bat html\n        ```\n      + _on Linux and MacOs_\n        ```\n            make html\n        ```\n  3. Open the `build/html/index.html` file with a web browser of your choice!\n\n## Acknowledgements\nThis work has been funded by the project “Open Biomedical Citations in Context Corpus”\n(Wellcome Trust, Grant n. 214471/Z/18/Z) and the project “Wikipedia Citations in Wikidata”\n(Wikimedia Foundation, https://meta.wikimedia.org/wiki/Wikicite/grant/Wikipedia_Citations_in_Wikidata).\n\nWe would like to thank (in alphabetic order) Fabio Mariani (@FabioMariani), Arcangelo\nMassari (@arcangelo7), and Gabriele Pisciotta (@GabrielePisciotta) for the constructive feedback.\n',
    'author': 'Silvio Peroni',
    'author_email': 'essepuntato@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://opencitations.net',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.4,<4.0.0',
}


setup(**setup_kwargs)
