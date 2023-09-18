"""
Template for the py project toml file
"""
# pylint: disable=W1401

EXTENSION = ".toml"
DIR = "./"
TEMPLATE = """

[tool]
[tool.poetry]
name = "{project_name}"
version = "0.2.9"
homepage = "https://github.com/{author}/{project_name}"
description = "A collection of tooling to enable open source development of autonomy tools"
authors = ["{author}"]
readme = "readme.md"
license =  "Apache-2.0"
classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
]
packages = [
    {{ include = "{project_name}" }},
]


[tool.poetry.dependencies]
python = ">=3.7.2,<=3.11"

[tool.poetry.dev-dependencies]


[tool.poetry.extras]
dev = ["pre-commit", "virtualenv", "pip", "twine", "toml", "bump2version"]
doc = [
    "mkdocs",
    "mkdocs-include-markdown-plugin",
    "mkdocs-material",
    "mkdocstrings",
    "mkdocs-material-extension",
    "mkdocs-autorefs"
    ]

[tool.poetry.scripts]
adev = 'auto_dev.cli:cli'

[tool.poetry.group.dev.dependencies]
twine = "^4.0.2"

[tool.black]
line-length = 120
skip-string-normalization = true
target-version = ['py37', 'py38', 'py39']
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 120
skip_gitignore = true
# you can skip files as below
#skip_glob = docs/conf.py

[build-system]
build-backend = "poetry.core.masonry.api"
requires = ["poetry-core>=1.0.0", "setuptools"]

"""
