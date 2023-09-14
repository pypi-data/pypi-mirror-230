# oaspy

[![Python: 3.10](https://img.shields.io/badge/python-3.10-blue?logo=python)](https://docs.python.org/3.10/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/oaspy.svg)](https://pypi.org/project/oaspy/)
---

**oaspy** is a quick-and-dirty tool to generate an [OpenApi 3.x](https://www.openapis.org) specification from an [insomnia V4](https://insomnia.rest/products/insomnia) collections. 


## Getting Started

For more, see the [documentation](./docs/README.md).

### Installation

**oaspy** is available on [PyPI](https://pypi.org/project/oaspy/):

```shell
pip install oaspy
```

## Usage

To run **oaspy**, try any of the following:

```sh
oaspy --help
```


## Commands

### **gen:** :new: (in progress)

Generate an OpenApi 3.x file from an Insomnia collection v4.

```sh
oaspy gen --help
```

with the default options.

```sh
oaspy gen --file Insomnia_file_v4.json
```

defining the version of openapi to generate.

```sh
oaspy gen --file Insomnia_file_v4.json --schema v30
```
> argument `v30` refers to openapi version 3.0.x

defining the version of openapi to generate and the output file name.

```sh
oaspy gen --file Insomnia_file_v4.json --output my_oa3_export.json
```

a complete version of the above.

```sh
oaspy gen --file Insomnia_file_v4.json --schema v30 --output my_oa3_export.json
```


### **check:** :new:

Validates the structure of an OpenApi file.

```sh
oaspy check --help
```

```sh
oaspy check --file my_oa3_export.json
```

### **info:** :new:

Shows information from an Insomnia v4 file.

```sh
oaspy info --help
```

```sh
oaspy info --file Insomnia_file_v4.json
```


### Configuration

**oaspy** can be configured through a `pyproject.toml` if it is used as a dev dependency in your project.

If left unspecified, the default configuration is equivalent to:

```toml
[tool.oaspy]
title = "awesome api - OpenAPI 3.0"
description = "my awesome api"
terms-of-service = "http://awesome.io/terms"
contact-url = "http://awesome.io"
contact-email = "apiteam@awesome.io"
license-name = "MIT"
license-url = "https://opensource.org/license/mit/"
version = "1.0.0"
```


## License

This project is licensed under the terms of the [MIT.](https://opensource.org/license/mit/) license.

The full text of this license can be found in the [LICENSE.](./LICENSE) file.


## How to Contribute

For any questions, comments, suggestions or contributions, go to the [issues.](https://gitlab.com/HomeInside/oaspy/-/issues) section.
Before opening a new issue, check the existing ones to find a solution (possibly already existing) to the problem you are facing.
