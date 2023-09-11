# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['majormode', 'majormode.perseus', 'majormode.perseus.agent']

package_data = \
{'': ['*']}

install_requires = \
['perseus-core-library>=1.19.4,<2.0.0',
 'perseus-getenv-library>=1.0.4,<2.0.0',
 'perseus-microrm-library>=1.3.4,<2.0.0']

setup_kwargs = {
    'name': 'perseus-agent-library',
    'version': '1.0.9',
    'description': 'Perseus Agent Python Library',
    'long_description': '# Perseus Agent Python Library\n\nPerseus Agent Python Library provides core classes to develop agents (workers) responsible for performing asynchronous tasks in the background.\n\nThese components have minimal dependencies on other libraries, so that they can be deployed easily.  In addition, these components will keep their interfaces as stable as possible, so that other Python projects can integrate these components without having to worry about changes in the future.\n\n\nTo install the Perseus Agent Python Library, enter the follow command line:\n\n```bash\n$ pipenv install perseus-agent-library\n```\n',
    'author': 'Daniel CAUNE',
    'author_email': 'daniel.caune@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/majormode/perseus-agent-python-library',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
