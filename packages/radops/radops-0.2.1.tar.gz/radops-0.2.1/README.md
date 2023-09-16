# R&D Ops

![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ekorman/d81291a17ab6b9da379c104040db96f2/raw/radops-coverage.json)

Docs: [https://striveworks.github.io/radops/](https://striveworks.github.io/radops/)

## Python package

### Install

```shell
pip install radops
```

### Dev setup

```shell
pip install -e ".[dev]"
pre-commit install
```

## Testing

### Unit tests

Unit tests can be run via

```shell
pytest tests/unit-tests
```

### Functional tests

Functional tests require s3 setup. This can be done locally via

```shell
docker run -p 9000:9000 -p 9090:9090 -e MINIO_ROOT_USER=user -e MINIO_ROOT_PASSWORD=password quay.io/minio/minio server /data --console-address ":9090"
```

and then the functional tests can be run using the following command

```shell
s3_endpoint_url=http://127.0.0.1:9000 aws_access_key_id=user aws_secret_access_key=password pytest -s tests/functional-tests/test_data_lake.py
```
