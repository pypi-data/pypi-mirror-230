<div align="center"><img alt="logo" src="./docs/_static/images/icon.png" width="70" /></div>

<h1 align="center">collective.bluesky</h1>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/collective.bluesky)](https://pypi.org/project/collective.bluesky/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/collective.bluesky)](https://pypi.org/project/collective.bluesky/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/collective.bluesky)](https://pypi.org/project/collective.bluesky/)
[![PyPI - License](https://img.shields.io/pypi/l/collective.bluesky)](https://pypi.org/project/collective.bluesky/)
[![PyPI - Status](https://img.shields.io/pypi/status/collective.bluesky)](https://pypi.org/project/collective.bluesky/)


[![PyPI - Plone Versions](https://img.shields.io/pypi/frameworkversions/plone/collective.bluesky)](https://pypi.org/project/collective.bluesky/)

[![Meta](https://github.com/collective/collective.bluesky/actions/workflows/meta.yml/badge.svg)](https://github.com/collective/collective.bluesky/actions/workflows/meta.yml)
![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000)

[![GitHub contributors](https://img.shields.io/github/contributors/collective/collective.bluesky)](https://github.com/collective/collective.bluesky)
[![GitHub Repo stars](https://img.shields.io/github/stars/collective/collective.bluesky?style=social)](https://github.com/collective/collective.bluesky)

</div>

**collective.bluesky** is a package providing a [Plone](https://plone.org/) content rules action to post a status to Bluesky.


# Installation

This package supports Plone sites using Volto and ClassicUI.

For proper Volto support, the requirements are:

* plone.restapi >= 8.34.0
* Volto >= 16.10.0

Add **collective.bluesky** to the Plone installation using `pip`:

```bash
pip install collective.bluesky
```

or add it as a dependency on your package's `setup.py`

```python
    install_requires = [
        "collective.bluesky",
        "Plone",
        "plone.restapi",
        "setuptools",
    ],
```

## Configuration

### Obtaining an App Password
Before you can use this package, you have to register an App Password on Bluesky.
To do so, log in to your account, visit [App Password](https://bsky.app/settings/app-passwords) and add a new `App Password`.
Go to the newly created application page and copy the value of `Your access token`.

### Configuring Plone

This package is configured via the `BLUESKY_APPS` environment variable which should contain a valid JSON array with your Bluesky Application information.

Each application registration requires the following information:

| Key | Description | Example Value |
| -- | -- | -- |
| host | Hostname of the instance to be used. Default value: `bsky.app` | sandbox.tld |
| handle | Handle used to log in the host (without the @) | demo |
| app_password | Application password | 1232434323234 |
| protocol | Host protocol. Default value: `https` | https |

Using the information above, the environment variable would look like:

```shell
BLUESKY_APPS='[{"host":"bsky.app","handle":"demo","app_password":"1232434323234"}]'
```

### Starting Plone

Now, you can start your local Plone installation with:

```shell
BLUESKY_APPS='[{"host":"bsky.app","handle":"demo","app_password":"1232434323234"}]' make start
```

or, if you are using a `docker compose` configuration, add the new environment variable under the `environment` key:

```yaml
    environment:
      - BLUESKY_APPS=[{"host":"bsky.app","handle":"demo","app_password":"1232434323234"}]
```

After start-up visit the `Content Rules` Control Panel, and create a new content rule.

No additional configuration is needed for Volto support.

# Contributing

If you want to help with the development (improvement, update, bug-fixing, ...) of `collective.bluesky` this is a great idea!

- [Issue Tracker](https://github.com/collective/collective.bluesky/issues)
- [Source Code](https://github.com/collective/collective.bluesky/)
- [Documentation](https://collective.github.io/collective.bluesky)

We appreciate any contribution and if a release is needed to be done on PyPI, please just contact one of us.

## Local Development

You need a working `python` environment (system, `virtualenv`, `pyenv`, etc) version 3.8 or superior.

Then install the dependencies and a development instance using:

```bash
make build
```
### Update translations

```bash
make i18n
```

### Format codebase

```bash
make format
```

### Run tests

Testing of this package is done with [`pytest`](https://docs.pytest.org/) and [`tox`](https://tox.wiki/).

Run all tests with:

```bash
make test
```

Run all tests but stop on the first error and open a `pdb` session:

```bash
./bin/tox -e test -- -x --pdb
```

Run only tests that match `TestAppDiscovery`:

```bash
./bin/tox -e test -- -k TestAppDiscovery
```

Run only tests that match `TestAppDiscovery`, but stop on the first error and open a `pdb` session:

```bash
./bin/tox -e test -- -k TestAppDiscovery -x --pdb
```

## Translations

This product has been translated into:

- English (Érico Andrei)
- Português do Brasil (Érico Andrei)

# License

The project is licensed under GPLv2.

# One Last Thing

Originally Made in São Paulo, Brazil, with love, by your friends @ Simples Consultoria.

Now maintained by the [Plone Collective](https://github.com/collective)
