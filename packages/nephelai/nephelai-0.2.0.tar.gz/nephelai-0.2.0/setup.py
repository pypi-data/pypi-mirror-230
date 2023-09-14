# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nephelai']

package_data = \
{'': ['*']}

modules = \
['py']
install_requires = \
['bitmath>=1.3.3.1,<2.0.0.0',
 'pyocclient>=0.6,<0.7',
 'python-dotenv>=1.0.0,<2.0.0',
 'tqdm>=4.65.0,<5.0.0',
 'typer>=0.9.0,<0.10.0',
 'typing-extensions>=4.7.1,<5.0.0']

extras_require = \
{'docs': ['mkdocs>=1.4.2,<2.0.0',
          'mkdocs-material>=9.0.9,<10.0.0',
          'mkdocstrings[python]>=0.20.0,<0.21.0',
          'mkdocs-literate-nav>=0.6.0,<0.7.0',
          'mkdocs-gen-files>=0.4.0,<0.5.0',
          'mkdocs-section-index>=0.3.5,<0.4.0']}

entry_points = \
{'console_scripts': ['nephelai = nephelai.main:app']}

setup_kwargs = {
    'name': 'nephelai',
    'version': '0.2.0',
    'description': 'A helper library to transport your data into the (next)cloud',
    'long_description': '<p align="center">\n<img src="https://github.com/dobraczka/nephelai/raw/main/docs/assets/logo.png" alt="nephelai logo", width=200/>\n<h2 align="center">nephelai</h2>\n</p>\n\n<p align="center">\n<a href="https://github.com/dobraczka/nephelai/actions/workflows/main.yml"><img alt="Actions Status" src="https://github.com/dobraczka/nephelai/actions/workflows/main.yml/badge.svg?branch=main"></a>\n<a href=\'https://nephelai.readthedocs.io/en/latest/?badge=latest\'><img src=\'https://readthedocs.org/projects/nephelai/badge/?version=latest\' alt=\'Documentation Status\' /></a>\n<a href="https://pypi.org/project/nephelai"/><img alt="Stable python versions" src="https://img.shields.io/pypi/pyversions/nephelai"></a>\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n</p>\n\nA helper library to upload/download files to/from a password-protected shared nextcloud folder. The link and password are read from your `.env` to enable project-specific shared folders.\nBecause Nextcloud does not enable chunked uploads for shared folders and your files can hit the size limit, your files are uploaded in chunks if needed and reconstructed after download.\n\nUsage\n=====\nCreate a `.env` file in your project root.\nRemember to add this file to your `.gitignore` and always keep it secure to keep your secrets!\nYour `.env` should contain:\n```bash\nNEXTCLOUD_FOLDER_URI="uri_of_the_shared_folder"\nNEXTCLOUD_FOLDER_PW="pw_of_the_folder"\n```\nThen you can interact with the folder in a variety of ways.\nAlternatively, you can set this environment variables yourself with your preferred method.\n\nVia CLI:\n--------\n```bash\nnephelai upload mytestfile.txt anextcloud/path/thatwillbecreatedifneeded/\nnephelai download anextcloud/path/thatwillbecreatedifneeded/mytestfile.txt\n```\nYou can also upload folders including the file structure:\n```bash\ntests/resources\n├── mymatrix.npy\n└── subfolder\n    └── testfile.txt\n```\nUsing the `upload-with-fs` command:\n```bash\nnephelai upload-with-fs tests/resources\n```\n\nWhich is just syntactic sugar for:\n\n```bash\nnephelai upload tests/resources tests/resources\n```\n\nDownloading can be done accordingly:\n```bash\nnephelai download tests\n```\nWhich will download it to your current directory. You can also specify the download path:\n\n```bash\nnephelai download tests --local-path /tmp/\n```\nThis download the folder as:\n```bash\n/tmp/tests\n└── resources\n    ├── mymatrix.npy\n    └── subfolder\n        └── testfile.txt\n```\n\nUsing \n\n```bash\nnephelai ls tests\n```\nyou can show the files in the `tests` directory.\n\nYou can get help for each command via the `--help` flag.\n\nVia Python:\n----------\n```python\nfrom nephelai import upload, download\n\nupload("tests/resources", "tests/resources")\nfile_dl_path = "/tmp/mymatrix.npy"\ndownload("tests/resources/mymatrix.npy",file_dl_path)\n\nimport numpy as np\n\nmymatrix = np.load(file_dl_path)\n```\n\nInstallation\n============\n\n`pip install nephelai`\n',
    'author': 'Daniel Obraczka',
    'author_email': 'obraczka@informatik.uni-leipzig.de',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/dobraczka/nephelai',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
