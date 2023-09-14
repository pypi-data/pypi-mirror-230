# FastAPI Request helper

## How to use

1. Set a variable

```python

# user_service.py
from fastapi import FastAPI
from fastapi_global_variable import GlobalVariable

app = FastAPI(title="Application")

GlobalVariable.set('app', app)
```

2. Use variable

```python
from fastapi_global_variable import GlobalVariable

print(GlobalVariable.get_or_fail('app'))
print(GlobalVariable.get('app'))
```

## How to test in testpypi

1. Increase the version in `pyproject.toml`
2. Run command

```bash
$ . ./build_and_test.sh
```

## How to publish new version

1. Increase the version in `pyproject.toml`
2. Run command

```bash
$ . ./build_and_publish.sh
```
