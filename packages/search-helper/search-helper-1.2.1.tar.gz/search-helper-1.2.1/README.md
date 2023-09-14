# Search Helper

_User-configurable, cross-platform Tk GUI
for opening predefined search URLs in a web browser._


## Installation


You can install the [package from PyPI](https://pypi.org/project/search-helper/):

```bash
pip install --upgrade search-helper
```

> Using a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
> is strongly recommended.


## Running from the source repository

If you decide to run from the checked out sources instead,
you have to install the requirements using

```bash
pip install --upgrade search-helper
```

and then set the environment variable `PYTHONPATH` to `src`:

### Linux / Unix

```bash
export PYTHONPATH=src
```

### Windows

```cmd
SET PYTHONPATH=src
```


## Usage

Choose the configuration file via a dialog:

```
python -m search_helper
```

Specify a configuration file on the command line:

```
python -m search_helper configfile.yaml
```


## Further reading

[→ Full documentation](https://blackstream-x.gitlab.io/search-helper/)
