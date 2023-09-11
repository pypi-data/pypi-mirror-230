# FastAPI Exception

### Setup python environment

```shell
python3 -m venv venv
```

### Active the python environemt

```shell
. venv/bin/activate
```

### Install requirements

```shell
pip install -r requirements.txt
```

## How to use

```python
# Init FastAPI

# config/exception.py
from config.i18n import i18n_service
from bootstraps import app
from fastapi_exception import FastApiException

FastApiException.init(app, i18n_service)
```
