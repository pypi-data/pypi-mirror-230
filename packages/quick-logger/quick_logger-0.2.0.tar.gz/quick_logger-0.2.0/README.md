

# `quick_logger`

A simple interface for the standard Python logging library.

## About

This is a very simple package designed to setup a logger in one line and allow logging to it with ease.

### Note

I wrote this package when I was still in school. It's really no easier than just using `logger.<level>`.

However, the `init_logger` method may still be of some use. I've updated it such that `mlog` can now 
be dispatched with level:
```
from quick_logger import mlog
# Previously any level beyond info:
mlog("Here's a debug message.", "debug")
# Now, can use the same idiom as `logger.<level>`:
mlog.debug("Here's a debug message.")
```
Note that the original syntax is still backward-compatible, on the offchace anything out there uses this.

Ultimately, this package is ***very*** simple, you probably just want to use the base Python logging library.

## Installation

Use pip to install.

```
python -m pip install quick_logger
```

## Usage

Use `init_logger` to create a log file, and `mlog` to add a log entry. 

### Quick Start

#### `init_logger`

```python
from quick_logger import init_logger, mlog

init_logger('/path/to/file.log')
```
By default, the log file will be set to `logging.INFO`.

#### `mlog`

``` python
# By default logs are set to "info"
mlog("Logged something!")
# Invoke by level
mlog.error("Something went wrong!")
```
It's that easy!

### "Advanced" Setup

You can set a *few* options when you use `init_logger`.
 - `level`: Defaults to `info`, accepts `critical`, `error`, `warning`, `info`, `debug`, `notset`. 
 - `fmt`: Defaults to `'%(asctime)s:: %(levelname)s:: %(message)s'`. See [logging.Formatter](https://docs.python.org/3/library/logging.html#logging.Formatter) for details on how to set a `Formatter` string.
 - `datefmt`: Defaults to `'%Y-%m-%d %H:%M:%S'`. See [strftime reference](https://strftime.org/).
 
``` python
from quick_logger import init_logger
# Log file set to debug
init_logger('/path/to/file.log', level='debug')
...
# Log file with fmt that includes module.
fmt = '%(asctime)s:: %(module)s:: %(message)s'
# or log file with fmt that just has messages.
fmt = '%(message)s'
init_logger('/path/to/file.log', fmt=fmt)
...
# Omit date, just include the time.
init_logger('/path/to/file.log', datefmt='%H:%M:%S')
```

## Issues/Suggestions

Please make any suggestions or issues on the Github page. Note that this package is meant to be simple, so suggestions should keep that in mind. 

## License

This project is licensed under the MIT License. Please see the LICENSE.md file for details.
