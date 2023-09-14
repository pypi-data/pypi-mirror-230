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
