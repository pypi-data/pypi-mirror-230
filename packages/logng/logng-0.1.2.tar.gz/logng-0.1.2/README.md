<div align=center>
  <img width=200 src="https://raw.githubusercontent.com/H2Sxxa/logng/main/doc/logo.png" alt="[logo](https://raw.githubusercontent.com/H2Sxxa/logng/main/doc/logo.png)"/>
  <h1 align="center">LogNG</h1>
</div>

<div align=center>
  <img src="https://img.shields.io/badge/python-3.8+-blue" alt="python">
  <img src="https://img.shields.io/github/languages/code-size/H2Sxxa/logng" alt="size">
  <img src="https://img.shields.io/github/license/H2Sxxa/logng" alt="license">
</div>

# What's this?

A logging library, intending to simplify the use of logger and easy to configure or implement.

# Install

```shell
pip install logng
```

# How to use

## logger

It's a implementation of the `ILogger`, with the high configurability.

```python
from logng.logger import Logger, LogConfig

lg = Logger()
lg.info("hello info")
```

## shared

You can implement `ILogger` yourself and set the logger here.

```python
from logng.shared import set_logger, info, warn
from logng.logger import Logger, LogConfig

set_logger(Logger())
info("hello")
warn("hello")
```