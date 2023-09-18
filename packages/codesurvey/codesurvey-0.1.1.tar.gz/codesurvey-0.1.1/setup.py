# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['codesurvey',
 'codesurvey.analyzers',
 'codesurvey.analyzers.python',
 'codesurvey.sources']

package_data = \
{'': ['*']}

install_requires = \
['astpath>=0.9.0,<0.10.0',
 'lxml>=4.9.1,<5.0.0',
 'peewee>=3.15.2,<4.0.0',
 'requests>=2.28.1,<3.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'codesurvey',
    'version': '0.1.1',
    'description': 'Analyse source code repositories for language feature and library usage.',
    'long_description': '<div align="center">\n\n<h1>CodeSurvey</h1>\n\n<a href="https://pypi.org/project/codesurvey">\n    <img alt="PyPI" src="https://img.shields.io/pypi/v/codesurvey">\n</a>\n\n<p>\n    <a href="https://github.com/when-of-python/codesurvey">GitHub</a> - <a href="https://when-of-python.github.io/codesurvey">Documentation</a>\n</p>\n\n</div>\n\nCodeSurvey is a framework and tool to survey code repositories for\nlanguage feature usage, library usage, and more:\n\n* Survey a specific set of repositories, or randomly sample\n  repositories from services like GitHub\n* Built-in support for analyzing Python code; extensible to support\n  any language\n* Write simple Python functions to define the code features you want\n  to survey; record arbitrary details of feature occurrences\n* Supports parallelizization of repository downloading and analysis\n  across multiple processes\n* Logging and progress tracking to monitor your survey as it runs\n* Inspect the results as Python objects, or in an sqlite database\n\n\n## Installation\n\n```\npip install codesurvey\n```\n\n\n## Usage\n\nThe `CodeSurvey` class can easily be configured to run a survey, such\nas to measure how often the `math` module is used in a random set of\nrecently updated Python repositories from GitHub:\n\n```python\nfrom codesurvey import CodeSurvey\nfrom codesurvey.sources import GithubSampleSource\nfrom codesurvey.analyzers.python import PythonAstAnalyzer\nfrom codesurvey.analyzers.python.features import py_module_feature_finder\n\n# Define a FeatureFinder to look for the `math` module in Python code\nhas_math = py_module_feature_finder(\'math\', modules=[\'math\'])\n\n# Configure the survey\nsurvey = CodeSurvey(\n    db_filepath=\'math_survey.sqlite3\',\n    sources=[\n        GithubSampleSource(language=\'python\'),\n    ],\n    analyzers=[\n        PythonAstAnalyzer(\n            feature_finders=[\n                has_math,\n            ],\n        ),\n    ],\n    max_workers=5,\n)\n\n# Run the survey on 10 repositories\nsurvey.run(max_repos=10)\n\n# Report on the results\nrepo_features = survey.get_repo_features(feature_names=[\'math\'])\nrepo_count_with_math = sum([\n    1 for repo_feature in repo_features if\n    repo_feature.occurrence_count > 0\n])\nprint(f\'{repo_count_with_math} out of {len(repo_features)} repos use math\')\n```\n\n![Animated GIF of CodeSurvey demo on the command-line](https://when-of-python.github.io/codesurvey/images/codesurvey-demo.gif)\n\n* For more Sources of repositories, see [Source\n  docs](https://when-of-python.github.io/codesurvey/sources/core)\n* For more Analyzers and FeatureFinders, see [Analyzer\n  docs](https://when-of-python.github.io/codesurvey/analyzers/core)\n* For more options and methods for inspecting results, see\n  [`CodeSurvey` docs](https://when-of-python.github.io/codesurvey/core)\n* For details on directly inspecting the sqlite database of survey\n  results see [Database docs](https://when-of-python.github.io/codesurvey/database)\n* More examples can be found in\n  [examples](https://github.com/when-of-python/codesurvey/tree/main/examples)\n\n\n## Contributing\n\n* Install Poetry dependencies with `make deps`\n* Documentation:\n    * Run local server: `make docs-serve`\n    * Build docs: `make docs-build`\n    * Deploy docs to GitHub Pages: `make docs-github`\n    * Docstring style follows the [Google style guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)\n\n\n## TODO\n\n* Add unit tests\n',
    'author': 'Ben Denham',
    'author_email': 'ben@denham.nz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/when-of-python/codesurvey',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
