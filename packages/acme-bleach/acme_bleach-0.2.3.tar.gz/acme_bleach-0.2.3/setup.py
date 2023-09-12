# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['acme', 'acme.bleach']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1,<9.0']

entry_points = \
{'console_scripts': ['bleach = acme.bleach.app:main']}

setup_kwargs = {
    'name': 'acme-bleach',
    'version': '0.2.3',
    'description': 'Remove unsightly non-whitespace characters from your code.',
    'long_description': '# Bleach\n\n[![Read the documentation at https://acme-bleach.readthedocs.io/](https://img.shields.io/readthedocs/acme-bleach/latest.svg?label=Read%20the%20Docs)][read the docs]\n\n[read the docs]: https://acme-bleach.readthedocs.io/\n[tests]: https://github.com/stefansm/acme-bleach/actions?workflow=Tests\n\nRemove unsightly visible characters from your code. Inspired by the [`Acme::Bleach` Perl module][acme::bleach] by Damian\nConway.\n\n[acme::bleach]: https://metacpan.org/pod/Acme::Bleach\n\n## Installation\n\nYou can install _Bleach_ via [pip] from [PyPI]:\n\n```console\n$ pip install acme-bleach\n```\n\n## Usage\n\nLet\'s start with the following Python script, `hello.py`:\n\n```python\nprint("Hello, world!")\n```\n\n### Bleaching\n\nTo bleach it, run the following command:\n\n```console\n$ bleach bleach hello.py -o hello-bleached.py\n```\n\nThe result is a bleached version of the original script. The contents of\n`hello-bleached.py` are (representing tabs with `»»»»` and spaces with `·`):\n\n```\n# coding=bleach\n»»»»···»»»»»»»»»»»»»»»»»···»»»»»·»»»»»»»··»»·»»»»»»»·»»»··»»···»»»»»···»·»»»»»»»\n»»»»»»»»·»»»·»»»»»»»»»»»»»»»»»»»·»»»»»»»»»»»·»»»»»»»·»»»»»»»·»»»»»»»»»»»»»»»··»»»»»»·»»»·»»»··»»··»»»»»»\n»»»»··»»··»»»»»»»»»»··»»····»»»»»»»»·»»»··»»»»»»»»»»»»»»·»»»»»»»»»»»»»»»»»»»»»»»···»···\n»»»»··»»····»»»»···»»»»»·»»»»»»»··»»··»»»»»»»»»»··»»»»»»·»»»»»»»»»»»»»»»·»»»»»»»»»»»»»»»·\n»»»»»»»»·»»»»»»»»»»»·»»»»»»»»»»»·»»»·»»»»»»»·»»»»»»»»»»»»»»»·»»»·»»»\n```\n\n### Running\n\nYou can run the bleached file using `bleach run`:\n\n```console\n$ bleach run hello-bleached.py\nHello, world!\n```\n\n### Unbleaching\n\nYou can unbleach the file using `bleach unbleach`:\n\n```console\n$ bleach unbleach hello-bleached.py -o hello-unbleached.py\n$ cat hello-unbleached.py\nprint("Hello, world!")\n```\n\n### Installing the bleach codec\n\nRunning scripts with `bleach run` is far too much effort. If you want to run bleached scripts directly, you can install\nthe `bleach` codec:\n\n```console\n$ bleach install\nWrote /home/stefans/bleach/.venv/lib/python3.10/site-packages/bleach.pth\n$ python hello-bleached.py\nHello, world!\n```\n\nInstalling the codec will attempt to write a `.pth` file to the `site-packages` directory of the current Python\ninterpreter. Note the `import` in the `.pth` file will be evaluated every time the current Python runs, so there is a\ntiny amount of overhead.\n\n## License\n\nDistributed under the terms of the [MIT license][license],\n_Bleach_ is free and open source software.\n\n## Credits\n\nThis project was generated from a variant of [@cjolowicz]\'s [Hypermodern Python Cookiecutter] template.\n\n[@cjolowicz]: https://github.com/cjolowicz\n[pypi]: https://pypi.org/\n[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[pip]: https://pip.pypa.io/\n\n<!-- github-only -->\n\n[license]: https://github.com/stefansm/acme-bleach/blob/main/LICENSE\n[command-line reference]: https://acme-bleach.readthedocs.io/en/latest/usage.html\n',
    'author': 'Stefans Mezulis',
    'author_email': 'stefans.mezulis@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/stefansm/acme-bleach',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
