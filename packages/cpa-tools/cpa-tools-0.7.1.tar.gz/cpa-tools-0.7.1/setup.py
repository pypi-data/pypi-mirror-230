# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cpa']

package_data = \
{'': ['*']}

install_requires = \
['anndata>=0.7.5',
 'llvmlite>=0.38.0,<0.39.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.21.5,<2.0.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'scvi-tools>=0.16.4',
 'seaborn>=0.11.2,<0.12.0']

extras_require = \
{':(python_version < "3.8") and (extra == "docs")': ['typing_extensions'],
 ':extra == "dev" or extra == "docs" or extra == "tutorials"': ['scanpy>=1.6'],
 ':extra == "docs" or extra == "tutorials"': ['toml>=0.10',
                                              'scipy>=1.8.0,<2.0.0'],
 ':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0'],
 'dev': ['black>=20.8b1',
         'codecov>=2.0.8',
         'flake8>=3.7.7',
         'isort>=5.7',
         'jupyter>=1.0',
         'loompy>=3.0.6',
         'nbconvert>=5.4.0',
         'nbformat>=4.4.0',
         'pre-commit>=2.7.1',
         'pytest>=4.4'],
 'docs': ['ipython>=7.1.1',
          'nbsphinx',
          'nbsphinx-link',
          'pydata-sphinx-theme>=0.4.0',
          'scanpydoc>=0.5',
          'sphinx>=4.1,<4.4',
          'sphinx-autodoc-typehints',
          'sphinx-rtd-theme'],
 'tutorials': ['leidenalg',
               'loompy>=3.0.6',
               'python-igraph',
               'scikit-misc>=0.1.3']}

setup_kwargs = {
    'name': 'cpa-tools',
    'version': '0.7.1',
    'description': 'Compositional Perturbation Autoencoder (CPA)',
    'long_description': '#  CPA - Compositional Perturbation Autoencoder [![PyPI version](https://badge.fury.io/py/cpa-tools.svg)](https://badge.fury.io/py/cpa-tools) [![Documentation Status](https://readthedocs.org/projects/cpa-tools/badge/?version=latest)](https://cpa-tools.readthedocs.io/en/latest/?badge=latest) [![Downloads](https://static.pepy.tech/badge/cpa-tools)](https://pepy.tech/project/cpa-tools)\n\n## What is CPA?\n\n![Alt text](https://user-images.githubusercontent.com/33202701/156530222-c61e5982-d063-461c-b66e-c4591d2d0de4.png?raw=true "Title")\n\n`CPA` is a framework to learn the effects of perturbations at the single-cell level. CPA encodes and learns phenotypic drug responses across different cell types, doses, and combinations. CPA allows:\n\n* Out-of-distribution predictions of unseen drug and gene combinations at various doses and among different cell types.\n* Learn interpretable drug and cell-type latent spaces.\n* Estimate the dose-response curve for each perturbation and their combinations.\n* Transfer pertubration effects from on cell-type to an unseen cell-type.\n\n\nUsage and installation\n-------------------------------\nSee [here](https://cpa-tools.readthedocs.io/en/latest/index.html) for documentation and tutorials.\n\n\nHow to optmize CPA hyperparamters for your data\n-------------------------------\n\n\nDatasets and Pre-trained models\n-------------------------------\nDatasets and pre-trained models are available [here](https://drive.google.com/drive/folders/1yFB0gBr72_KLLp1asojxTgTqgz6cwpju?usp=drive_link).\n\n\nSupport and contribute\n-------------------------------\nIf you have a question or new architecture or a model that could be integrated into our pipeline, you can\npost an [issue](https://github.com/theislab/cpa/issues/new)\n\nReference\n-------------------------------\n\n\nIf CPA is helpful in your research, please consider citing the  [Lotfollahi et al. 2023](https://www.embopress.org/doi/full/10.15252/msb.202211517)\n\n\n    @article{lotfollahi2023predicting,\n        title={Predicting cellular responses to complex perturbations in high-throughput screens},\n        author={Lotfollahi, Mohammad and Klimovskaia Susmelj, Anna and De Donno, Carlo and Hetzel, Leon and Ji, Yuge and Ibarra, Ignacio L and Srivatsan, Sanjay R and Naghipourfar, Mohsen and Daza, Riza M and \n        Martin, Beth and others},\n        journal={Molecular Systems Biology},\n        pages={e11517},\n        year={2023}\n    }\n\n',
    'author': 'Mohsen Naghipourfar',
    'author_email': 'naghipourfar@berkeley.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theislab/cpa/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.2,<3.11',
}


setup(**setup_kwargs)
