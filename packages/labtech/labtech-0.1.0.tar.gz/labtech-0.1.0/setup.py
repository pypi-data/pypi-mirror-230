# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['labtech']

package_data = \
{'': ['*']}

install_requires = \
['tqdm>=4.64.1,<5.0.0']

setup_kwargs = {
    'name': 'labtech',
    'version': '0.1.0',
    'description': 'Easily run experiment permutations with multi-processing and caching.',
    'long_description': '<div align="center">\n\n<h1>labtech</h1>\n\n<a href="">\n    <img alt="PyPI" src="https://img.shields.io/pypi/v/labtech">\n</a>\n\n<p>\n    <a href="https://github.com/ben-denham/labtech">GitHub</a> - <a href="https://ben-denham.github.io/labtech">Documentation</a>\n</p>\n\n</div>\n\nLabtech makes it easy to define multi-step experiment pipelines and\nrun them with maximal parallelism and result caching:\n\n* **Defining tasks is simple**; write a class with a single `run()`\n  method and parameters as dataclass-style attributes.\n* **Flexible experiment configuration**; simply create task objects\n  for all of your parameter permutations.\n* **Handles pipelines of tasks**; any task parameter that is itself a\n  task will be executed first and make its result available to its\n  dependent task(s).\n* **Implicit parallelism**; Labtech resolves task dependencies and\n  runs tasks in sub-processes with as much parallelism as possible.\n* **Implicit caching and loading of task results**; configurable and\n  extensible options for how and where task results are cached.\n\n\n## Installation\n\n```\npip install labtech\n```\n\n\n## Usage\n\n```python\nfrom time import sleep\n\nimport labtech\n\n# Decorate your task class with @labtech.task:\n@labtech.task\nclass Experiment:\n    # Each Experiment task instance will take `base` and `power` parameters:\n    base: int\n    power: int\n\n    def run(self):\n        # Define the task\'s run() method to return the result of the experiment:\n        labtech.logger.info(f\'Raising {self.base} to the power of {self.power}\')\n        sleep(1)\n        return self.base ** self.power\n\n# Configure Experiment parameter permutations\nexperiments = [\n    Experiment(\n        base=base,\n        power=power,\n    )\n    for base in range(5)\n    for power in range(5)\n]\n\n# Configure a Lab to run the experiments:\nlab = labtech.Lab(\n    # Specify a directory to cache results in (running the experiments a second\n    # time will just load results from the cache!):\n    storage=\'demo_lab\',\n    # Control the degree of parallelism:\n    max_workers=5,\n)\n\n# Run the experiments!\nresults = lab.run_tasks(experiments)\nprint([results[experiment] for experiment in experiments])\n```\n\n![Animated GIF of labtech demo on the command-line](https://ben-denham.github.io/labtech/images/labtech-demo.gif)\n\nLabtech can also produce graphical progress bars in\n[Jupyter](https://jupyter.org/) when the `Lab` is initialized with\n`notebook=True`:\n\n![Animated GIF of labtech demo in Jupyter](https://ben-denham.github.io/labtech/images/labtech-demo-jupyter.gif)\n\nTasks parameters can be any of the following types:\n\n* Simple scalar types: `str`, `bool`, `float`, `int`, `None`\n* Collections of any of these types: `list`, `tuple`, `dict`, `Enum`\n* Task types: A task parameter is a "nested task" that will be\n  executed before its parent so that it may make use of the nested\n  result.\n\nHere\'s an example of defining a single long-running task to produce a\nresult for a large number of dependent tasks:\n\n```python\nfrom time import sleep\n\nimport labtech\n\n@labtech.task\nclass SlowTask:\n    base: int\n\n    def run(self):\n        sleep(5)\n        return self.base ** 2\n\n@labtech.task\nclass DependentTask:\n    slow_task: SlowTask\n    multiplier: int\n\n    def run(self):\n        return self.multiplier * self.slow_task.result\n\nsome_slow_task = SlowTask(base=42)\ndependent_tasks = [\n    DependentTask(\n        slow_task=some_slow_task,\n        multiplier=multiplier,\n    )\n    for multiplier in range(10)\n]\n\nlab = labtech.Lab(storage=\'demo_lab\')\nresults = lab.run_tasks(dependent_tasks)\nprint([results[task] for task in dependent_tasks])\n```\n\nTo learn more, see:\n\n* [The API reference for Labs and Tasks](https://ben-denham.github.io/labtech/core)\n* [More options for cache formats and storage providers](https://ben-denham.github.io/labtech/caching)\n* [More examples](https://github.com/ben-denham/labtech/tree/main/examples)\n\n\n## Mypy Plugin\n\nFor [mypy](https://mypy-lang.org/) type-checking of classes decorated\nwith `labtech.task`, simply enable the labtech mypy plugin in your\n`mypy.ini` file:\n\n```INI\n[mypy]\nplugins = labtech/mypy_plugin.py\n```\n\n## Contributing\n\n* Install Poetry dependencies with `make deps`\n* Run linting, mypy, and tests with `make check`\n* Documentation:\n    * Run local server: `make docs-serve`\n    * Build docs: `make docs-build`\n    * Deploy docs to GitHub Pages: `make docs-github`\n    * Docstring style follows the [Google style guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)\n\n## TODO\n\n* Add unit tests\n',
    'author': 'Ben Denham',
    'author_email': 'ben@denham.nz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ben-denham/labtech',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
