# Development Setup

- [Development Setup](#development-setup)
  - [Setup Prerequisites](#setup-prerequisites)
    - [Mac](#mac)
    - [Ubuntu](#ubuntu)
    - [Windows](#windows)
  - [Install hcs-cli from local repo](#install-hcs-cli-from-local-repo)
  - [Create a new command](#create-a-new-command)
    - [Add a command file](#add-a-command-file)
    - [Run the new command](#run-the-new-command)
    - [Run Test](#run-test)
    - [Lint Code](#lint-code)
  - [Publish to PyPI](#publish-to-pypi)
    - [Prepare authentication to pypi](#prepare-authentication-to-pypi)
    - [Before Publish](#before-publish)
    - [Publish](#publish)
  - [References](#references)
    - [Command Return Value](#command-return-value)
      - [Specify Return Value](#specify-return-value)
      - [Return error with non-zero return code](#return-error-with-non-zero-return-code)
    - [Customize Output](#customize-output)
      - [Customize Output Format](#customize-output-format)
      - [Customize Output Fields](#customize-output-fields)
    - [IO Convention](#io-convention)
      - [Parameter \& Input](#parameter--input)
      - [Return Code](#return-code)
      - [Output](#output)
      - [Exception](#exception)


## Setup Prerequisites
### Mac
```zsh
brew update
brew install python3
python3 --version
python3 -m ensurepip
pip3 --version
# Test HCS CLI installed
hcs --version
```

### Ubuntu
```bash
sudo apt update
sudo apt install python3 -y
python3 --version
sudo apt install python3-pip -y
pip3 --version
# By default, on Ubuntu, python setup will not put hcs cli executable to
# the generic /usr/local/bin, but ~/.local/bin, which is not on the path.
# Add it to the path:
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
# Test HCS CLI installed
hcs --version
```

### Windows
Install python 3.11 from Windows App Store, then:
```bash
pip install hcs-cli
```
With default installation, it will show a message like:
```
WARNING: The script xxx is installed in 'C:\Users\xxx\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_xxxxx\LocalCache\local-packages\Python311\Scripts' which is not on PATH.
```
Add that path above to system or user path.

## Install hcs-cli from local repo
To develop hcs-cli code and use local source code:

Update dependencies
```bash
pip3 install -r requirements-dev.txt
```

Install the CLI from local source repo, so any change takes effect immediately via the "hcs" command:
```bash
make devinstall
```

then

```bash
hcs --version
```

## Create a new command

### Add a command file
This tutorial introduces how to add a new subgroup, and add a new command in that group.

1. Create a new folder "dev" in "vhcs/cli/cmds"
2. Create a new file "hello.py" in the new folder "vhcs/cli/cmds/dev/hello.py", with the following content:


```python
import click
 
@click.command()
@click.argument("name", type=str, required=True)
def hello(name: str):
    """Say hello"""
    return {
        "hello": name
    }
```

### Run the new command
```bash
hcs dev hello mortal
```

You should get:
```
{
    "hello": "mortal"
}
```
If the command is not found, refer to section [Install hcs-cli from local repo](#install-hcs-cli-from-local-repo)

### Run Test
```
make test
```

### Lint Code
hcs-cli uses the black style without customization. We have more important things than style debating to worry about.
```
make lint
```

## Publish to PyPI
### Prepare authentication to pypi
Create the pypi config file

vi ~/.pypirc
Put the following content, and save the file.
```ini
[distutils]
  index-servers =
    pypi
    hcs-cli
 
[pypi]
  username = __token__
  password = # either a user-scoped token or a project-scoped token you want to set as the default
 
[hcs-cli]
  repository = https://upload.pypi.org/legacy/
  username = __token__
  password = <an-auth-token-ask-dev-to-join-the-project-and-generate-your-own>
```
### Before Publish
* Update version in setup.py.
* Make sure UT and installation test pass.

### Publish
```
make release
```

## References

### Command Return Value

#### Specify Return Value
The default function return will be handled as data object and formated as CLI output. The output is formated according to common output parameters "–output" (e.g. json, yaml, etc).

Example of a command, which get an LCM template by ID:

```python
import click
from vhcs.service import lcm
 
@click.command()
@click.argument("id", type=str, required=True)
def get(id: str):
    """Get template by ID"""
    return lcm.template.get(id)
```

#### Return error with non-zero return code
If a failure case is encountered, the CLI should return a non-zero return code per convention. The second return value, if exists and is integer, will be used as return value.
In such error scenario, the output will be printed to STDERR, instead of STDOUT.
```python
@click.command()
def demoerror():
    """Demo error return"""
    my_shell_return_code = 123
    return "something wrong", my_shell_return_code
```

Or alternatively:
```python
import vhcs.common.ctxp as ctxp
@click.command()
def demoerror():
    """Demo error return"""
  return ctxp.error("Only set or get should be specified.")
```

By default, if an exception is thrown from a command function, it is considered as error and the CLI will have a non-zero return code.

### Customize Output

#### Customize Output Format

  * There are common parameters to control output format:

  * --output <json | yaml | text>
  * -o  <json | yaml | text>

  Example:

  * hcs -o=yaml admin template get <id>

#### Customize Output Fields

Instead of output the full json, which is normally large, use the --field argument to selectively keep fields to output.

  * --field <comma separated field names>
  * -f <comma separated field names>

Schema:

  * hcs --field <comma-separated-field-names> <subcommand> [ ... ]

Example:

  * hcs --field id,name lcm template get ras-07110204-2047
  * hcs --field id,name lcm template list

For advanced output manipulation, use the "jq" tool.

Examples:

  * hcs admin template list | jq ".[] | count"
  * hcs admin template list | jq ".[] | map(.id)"


### IO Convention

This section describes the convention & parameters that apply to all subcommands.

#### Parameter & Input
* Unix default double dash.
* Support STDIN for file-based input.

#### Return Code
  * 0: successful execution
  * Non-zero: problematic execution
#### Output
  * STDOUT for output
  * STDERR for error details
  * JSON format by default. Overridable to human-readable or yaml

#### Exception
* For known cases, exception & stack trace should be avoided. E.g. anticipated IO failures
* For unknown cases, exception & stack track must NOT be omitted and should be printed to STDERR.