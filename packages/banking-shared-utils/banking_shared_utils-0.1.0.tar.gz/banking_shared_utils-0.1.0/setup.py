#
import setuptools
from setuptools import setup


metadata = {'name': 'banking_shared_utils',
            'maintainer': 'Edward Azizov',
            'maintainer_email': 'edazizovv@gmail.com',
            'description': 'Shared extensions for MoneyPortal infrastructure',
            'license': 'Proprietary',
            'url': 'https://pypi.org/project/banking_shared_utils/',
            'download_url': 'https://pypi.org/project/banking_shared_utils/',
            'packages': setuptools.find_packages(),
            'include_package_data': True,
            'version': '0.1.0',
            'long_description': '',
            'python_requires': '>=3.10',
            'install_requires': []}

setup(**metadata)
