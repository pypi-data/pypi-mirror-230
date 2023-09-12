# aliyun-sls-logger

`aliyun-sls-logger` is an implementation of asynchronous Aliyun logging designed to integrate with asynchronous code. This library provides no additional features beyond logging.

## Installation

To install `aliyun-sls-logger`, simply use pip:

```
pip install aliyun-sls-logger
```

## Usage

To use `aliyun-sls-logger`, create an instance of the `QueuedLogHandler` class and add it to your logger. The `QueuedLogHandler` requires the following parameters:

* `access_key_id`: The access key ID for your Aliyun account.
* `access_key_secret`: The access key secret for your Aliyun account.
* `endpoint`: The endpoint for your Aliyun SLS service.
* `project`: The name of the project to log to.
* `logstore`: The name of the logstore to log to.

Once you have created an instance of the `QueuedLogHandler`, you can add it to your logger like any other handler:

```python
from aiologger import Logger
from aiologger.levels import LogLevel
from aliyun_sls_logger.logger_handler import QueuedLogHandler

logger = Logger(name=__name__, level=LogLevel.INFO)
handler = QueuedLogHandler(
    access_key_id='your_access_key_id',
    access_key='your_access_key_secret',
    end_point='your_endpoint',
    project='your_project',
    log_store='your_logstore',
    extract_json=True,
    extract_json_prefix='test_'
)
logger.add_handler(handler)

```

You can then use the logger as usual:

```python
await logger.info('This is a log message.')
```

