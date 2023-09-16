test-minio:
	docker run -d -p 9000:9000 -p 9090:9090 -e MINIO_ROOT_USER=user -e MINIO_ROOT_PASSWORD=password quay.io/minio/minio server /data --console-address ":9090"
functional-tests:
	s3_endpoint_url=http://127.0.0.1:9000 aws_access_key_id=user aws_secret_access_key=password pytest -v tests/functional-tests
unit-tests:
	s3_endpoint_url="" pytest -v tests/unit-tests
serve-docs:
	mkdocs serve
coverage:
	s3_endpoint_url="" COVERAGE_FILE=.coverage.unit coverage run --source=radops -m pytest -v tests/unit-tests
	s3_endpoint_url="" COVERAGE_FILE=.coverage.doctest coverage run -m doctest -v docs/serialization.md
	s3_endpoint_url=http://127.0.0.1:9000 aws_access_key_id=user aws_secret_access_key=password COVERAGE_FILE=.coverage.functional coverage run --source=radops -m pytest -v tests/functional-tests
	coverage combine
	coverage report
