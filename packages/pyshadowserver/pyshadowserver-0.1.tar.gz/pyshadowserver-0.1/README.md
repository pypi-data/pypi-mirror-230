# Pyshadowserver

[![PyPI](https://img.shields.io/pypi/v/pyshadowserver)](https://pypi.org/project/pyshadowserver/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/pyshadowserver)](https://pypistats.org/packages/pyshadowserver) [![PyPI - License](https://img.shields.io/pypi/l/pyshadowserver)](LICENSE) [![GitHub issues](https://img.shields.io/github/issues/te-k/pyshadowserver)](https://github.com/Te-k/pyshadowserver/issues)

Python library to interact with the [Shadow Server](https://www.shadowserver.org/what-we-do/network-reporting/) [Report API](https://github.com/The-Shadowserver-Foundation/api_utils/wiki).

So far it only implements the ASN, malware, Trusted Programs and report queries.

## API

See the [documentation](https://github.com/The-Shadowserver-Foundation/api_utils/wiki) and the source code for more information.

### Unauthenticated queries

```py
from pyshadowserver import ShadowServer, ShadowServerException

ss = ShadowServer()

ss.asn(origin="8.8.8.8")
ss.trusted_program("7fe2248de77813ce850053ed0ce8a474")

```

### Querying reports

```py
from pyshadowserver import ShadowServer, ShadowServerException

ss = ShadowServer(APIKEY, APISECRET)

# Find all reports and save them
reports = ss.reports_list()
for r in reports:
    data = ss.reports_download_raw(r["id"])
    with open(r["file"], "w+") as f:
        f.write(data)
```

## License

This code is published under MIT license: do whatever you want with it, but don't blame me if it fails (and open a PR)
