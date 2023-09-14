# About

[collective.bluesky](https://github.com/collective/collective.bluesky) is a package providing a [Plone](https://plone.org) content rules action to post a status using a Bluesky account.

## Code Health
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
      - BLUESKY_APPS='[{"host":"bsky.app","handle":"demo","app_password":"1232434323234"}]'
```

After start-up visit the `Content Rules` Control Panel, and create a new content rule.

No additional configuration is needed for Volto support.
