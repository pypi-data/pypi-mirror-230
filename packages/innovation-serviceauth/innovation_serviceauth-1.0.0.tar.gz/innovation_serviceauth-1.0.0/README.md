# Innovation Service Auth Python

This is a Python package for Indico Innovation developers import in their Python application in order to connect it to [Innovation Identity and Access Manager (IAM)](https://github.com/INDICO-DATA/innovation_iam).

## Requirements

* Python 3.10 or higher

## Dependencies

* gRPC
* jwcrypto

## Installation

To install this package simply run:

```bash
pip install innovation_serviceauth
```

## Usage

After that import in your Python application.

```python
import innovation_serviceauth as serviceauth


client = serviceauth.new_client()
```

There are some environment variables you must export:

> AUTH_SERVER = Innovation IAM host

> INNOVATION_CREDENTIALS = Service Account Key file to have permission

> INSECURE = true/false if you want to open a secure connection or not

## Setup and Develop

First of all read [Innovation Development Guidelines](https://github.com/INDICO-INNOVATION/innovation_team_guides) before contributing in this package.

Clone this repository and run commands bellow to create a Python virtual environment and install requirements.

```python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

After that make your changes and test it very well. For testing create a Python file (see [Usage](#usage) as example) e in a different path with its own virtual environment and run:

```bash
pip install -e <PATH_TO_PACKAGE>

# Overwrite <PATH_TO_PACKAGE> by directory path where you cloned this repository.
```

## License

Please, read [license](./LICENSE).
