# Helm Sign

`helm-cli` is a small tool which allows for creating signatures for packed Helm charts.
`helm` already offers an option for singing in verifying charts,
however it lacks support for using an existing GnuPG environment (see https://github.com/helm/helm/issues/7599).

![PyPI](https://img.shields.io/pypi/v/helm-sign?color=green)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/helm-sign)
![coverage report](https://gitlab.com/MatthiasLohr/helm-sign/badges/main/coverage.svg)
![PyPI - License](https://img.shields.io/pypi/l/helm-sign)
![PyPI - Downloads](https://img.shields.io/pypi/dm/helm-sign)


## Usage

### Install

`helm-sign` is available in the Python Package Index (PyPI).
Use the following command for installation:

```
pip install helm-sign
```


### Sign

`helm-sign` directly works on an already packed Helm chart (compressed tar file).

Simple usage:
```
helm-sign your-chart-1.0.0.tgz
```

For options on how to define the key to be use, run `helm-sign -h`.


### Verify Signature

`helm verify` needs the public key to be verified against in binary format.
Therefore, this is how verification can be done:

```bash
cd `mktemp -d`
# download public key (Matthias Lohr) and convert to binary format
curl https://keys.openpgp.org/vks/v1/by-fingerprint/F4A091E1F243C3748FFF661A8FC3060F80C31A0A | gpg --dearmor > mlohr.gpg
# download chart and provenance (signature) file
wget https://helm-charts.mlohr.com/hcloud-cloud-controller-manager/hcloud-cloud-controller-manager-2.0.0.tgz
wget https://helm-charts.mlohr.com/hcloud-cloud-controller-manager/hcloud-cloud-controller-manager-2.0.0.tgz.prov
# verify using helm CLI
helm verify --keyring ./mlohr.gpg hcloud-cloud-controller-manager-2.0.0.tgz
```

## License

This project is published under the Apache License, Version 2.0.
See [LICENSE.md](https://gitlab.com/MatthiasLohr/helm-sign/-/blob/master/LICENSE.md) for more information.

Copyright (c) by [Matthias Lohr](https://mlohr.com/) &lt;[mail@mlohr.com](mailto:mail@mlohr.com)&gt;
