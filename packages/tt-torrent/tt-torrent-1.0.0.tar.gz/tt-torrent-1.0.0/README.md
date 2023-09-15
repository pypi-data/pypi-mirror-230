<div align="center">
<img src="https://static.scarf.sh/a.png?x-pxid=cf317fe7-2188-4721-bc01-124bb5d5dbb2" />

## <img src="https://github.com/SantiiRepair/tt-torrent/blob/main/.github/images/logo.png?raw=true" height="56"/>


**😈 Daemon to manage torrents through tt-torrent website.**

______________________________________________________________________

[![License](https://img.shields.io/badge/License-Boost_1.0-magenta.svg)](https://www.boost.org/LICENSE_1_0.txt)
[![PyPI version](https://d25lcipzij17d.cloudfront.net/badge.svg?id=py&r=r&ts=1683906897&type=6e&v=1.0.0&x2=0)](https://pypi.org/project/quotexpy)
![GithubActions](https://github.com/SantiiRepair/tt-torrent/actions/workflows/pylint.yml/badge.svg)

</div>

______________________________________________________________________

## Installing

😈 **tt-torrent** is tested on Ubuntu 18.04 and Windows 10 with **python >= 3.10, <= 3.11.**.
```bash
pip install tt-torrent
```

If you plan to code and make changes, clone and install it locally.

```bash
git clone https://github.com/SantiiRepair/tt-torrent.git
pip install -e .
```

### Import
```python
from tttorrent.new.client import NewClient
```

### Authentication

```python
from tttorrent.new.client import NewClient

client = NewClient(email="user@email.com", password="password")
await client.auth()
client.close()
```

### Uploading torrent

```python
from tttorrent.new.client import NewClient

client = NewClient(email="user@email.com", password="password")
creds = await client.auth()
if not creds:
    sys.exit(print(colored("[ERROR]: Something wrong has happpened while authenticate", "red")))
with open("/path/to/description_text_file", "r") as f:
    description = f.read()
    f.close()
url = await client.upload(
    category=category,
    torrent_path="/path/to/torrent_file",
    image_path="/path/to/image_file",
    description=description,
)

print(url) 
client.close()
```