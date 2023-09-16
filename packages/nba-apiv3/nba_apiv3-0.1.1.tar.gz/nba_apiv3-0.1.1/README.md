[![PyPI](https://img.shields.io/pypi/v/nba_apiv3)](https://pypi.python.org/pypi/nba_apiv3)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/shufinskiy/nba_apiv3/blob/master/LICENSE)
[![Downloads](https://static.pepy.tech/badge/nba_apiv3)](https://pepy.tech/project/nba_apiv3)
[![Telegram](https://img.shields.io/badge/telegram-write%20me-blue.svg)](https://t.me/brains14482)

# nba_apiv3

## An API Client package to access the APIs version 3 for NBA.com

`nba_apiv3` is an API Client for `www.nba.com`. This package intends to make the APIs of [NBA.com](https://www.nba.com/) easily accessible and provide extensive documentation about them.

`nba_apiv3` is fork `nba_api` [package](https://github.com/swar/nba_api) and contains only endpoints that work with API version 3.

`nba_apiv3` contains two endpoints, which not work in `nba_api`:
  - [BoxScoreDefensiveV2](https://github.com/shufinskiy/nba_apiv3/blob/master/docs/nba_api/stats/endpoints/boxscoredefensivev2.md)
  - [BoxScoreMatchupsV3](https://github.com/shufinskiy/nba_apiv3/blob/master/docs/nba_api/stats/endpoints/boxscorematchupsv3.md)

# Getting Started

`nba_apiv3` requires Python 3.7+ along with the `requests` and `numpy` packages. While `pandas` is not required, it is required to work with Pandas DataFrames.

```bash
pip install nba_apiv3
```

## NBA 

```python
from nba_apiv3.stats.endpoints import boxscorematchupsv3

matchups = boxscorematchupsv3.BoxScoreMatchupsV3(game_id='0021700807')

## players stats
matchups.get_data_frames()[0]
```


# Documentation

- [Endpoints](/docs/nba_api/stats/endpoints)

# Contributing

*See [Contributing to the NBA_APIV3](https://github.com/shufinskiy/nba_apiv3/blob/master/CONTRIBUTING.md) for complete details.*

## Bugs

Encounter a bug, [report a bug](https://github.com/shufinskiy/nba_apiv3/issues).

# License & Terms of Use

## API Client Package

The `nba_apiv3` package is Open Source with an [MIT License](https://github.com/shufinskiy/nba_apiv3/blob/master/LICENSE).

## NBA.com

NBA.com has a [Terms of Use](https://www.nba.com/termsofuse) regarding the use of the NBA’s digital platforms.
