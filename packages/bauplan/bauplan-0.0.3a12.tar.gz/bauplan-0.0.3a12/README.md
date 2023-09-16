# Bauplan CLI

## Requirements

- [direnv](https://direnv.net/)
- [nix](https://nixos.org)
- [devenv](https://devenv.sh/)

## Package publication

Currently wheel is only supported on OSX with arm64

First compile dependency binaries (the actual CLI)

```bash
$ python build.py
...
```

To build the poetry package:

```bash
$ poetry build
...
```

To publish, first bump the version, then run `publish`

```bash
$ python build.py && poetry -vvv publish -u __token__ -p pypi-blahblahblah --build
...
```
