from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ul-py-tool',
    version='1.15.43',
    description='Python ul py tool',
    author='Unic-lab',
    author_email='',
    url='https://gitlab.neroelectronics.by/unic-lab/libraries/common-python-utils/ul-py-tool.git',
    packages=find_packages(include=['ul_py_tool*']),
    platforms='any',
    package_data={
        '': [
            'conf/*',
        ],
        'ul_py_tool': [
            'py.typed',
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            'ulpytool=ul_py_tool.main:main',
        ],
    },
    include_package_data=True,
    install_requires=[
        "numpy==1.23.3",
        "pandas==1.4.3",
        "pydantic[mypy]==1.10.2",
        "PyYAML==6.0",
        "colored==1.4.3",
        "rich==12.6.0",
        "tomli==2.0.1",
        "requests==2.28.1",

        "deepdiff==5.8.1",

        "mypy==0.982",
        "types-pyyaml==6.0.11",
        "types-pytz==2022.1.2",
        "types-python-dateutil==2.8.19",
        "types-setuptools==63.4.0",
        "typing-extensions==4.3.0",
        "data-science-types==0.2.23",
        "types-requests==2.28.8",
        "sphinx==7.2.6",

        "pycodestyle==2.9.1",
        "flake8==5.0.4",
        "flake8-commas==2.1.0",
        "flake8-noqa==1.2.8",
        "flake8-polyfill==1.0.2",
        "flake8-blind-except==0.2.1",
        "flake8-tidy-imports==4.8.0",
        "flake8-self==0.2.2",
        "flake8-super-call==1.0.0",
        "flake8-bugbear==22.7.1",
        "flake8-print==5.0.0",
        "pep8-naming==0.13.1",  # flask plugin
        "isort[colors]==5.10.1",
        "black==22.10.0",
        "yamllint==1.28.0",
        "ruff==0.0.198",

        "pytest==7.1.3",
        "pytest-cov==3.0.0",
        "python-gitlab==3.8.0",
        "kubernetes==23.6.0",

        "wheel==0.37.1",
        "twine==4.0.1",
        "setuptools==63.4.2",
    ],
)
