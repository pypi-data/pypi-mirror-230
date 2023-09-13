# Development

- Setup
  - Install venv with requirements from `setup.py`. 
  - Get proto files:
    - [google/rpc/status.proto](https://bb.yandexcloud.net/projects/CLOUD/repos/private-api/browse/third_party/googleapis/google/rpc/status.proto) 
    - [google/api/http.proto](https://bb.yandexcloud.net/projects/CLOUD/repos/private-api/browse/third_party/googleapis/google/api/http.proto)
    - [google/api/annotations.proto](https://bb.yandexcloud.net/projects/CLOUD/repos/private-api/browse/third_party/googleapis/google/api/annotations.proto)
    - [yandexproto/operation.proto](https://bb.yandexcloud.net/projects/CLOUD/repos/private-api/browse/yandex/cloud/priv/operation/operation.proto)
    - [yandexproto/validation.proto](https://bb.yandexcloud.net/projects/CLOUD/repos/private-api/browse/yandex/cloud/priv/validation.proto)
    - [yandexproto/operation_service.proto](https://bb.yandexcloud.net/projects/CLOUD/repos/datasphere/browse/backend/operations-api/src/main/proto/yandex/cloud/priv/datasphere/v1/operation_service.proto)
    - [yandexproto/job.proto](https://bb.yandexcloud.net/projects/CLOUD/repos/datasphere/browse/backend/jobs-api/src/main/proto/yandex/cloud/priv/datasphere/v2/jobs/jobs.proto?at=10eb0edf2c2697c6046c6d6dcedb7d75eef7168d)
    - [yandexproto/project_job_service.proto](https://bb.yandexcloud.net/projects/CLOUD/repos/datasphere/browse/backend/lobby-api/src/main/proto/yandex/cloud/priv/datasphere/v2/jobs/project_job_service.proto?at=10eb0edf2c2697c6046c6d6dcedb7d75eef7168d)
  - Run `build_proto.sh` to generate Protobuf wrappers.
- Unit tests
  - Run them from `tests/` using pytest.
  - Use `pytest-recording` and `pytest --block-network` to block potential network requests in tests.
- E2E tests
  - In these tests we launch client on real server and check expected results.
  - `cd tests_e2e/`.
  - Create venv installing this package as editable (`pip install -e ..`). Further steps are performed in this venv.
  - If you run Python program, install additional pip libraries which your script uses (i.e. `pip install pandas`).
  - Further steps depends on server environment. Possible cases are:
    - `DEV` environment – we use simple server mock, written in Python here in this repo.
      - Run server mock. See `python servermock/main.py --help` to see how to launch server. 
        You will have to specify S3 storage data to generate presigned URLs for client. 
    - `PREPROD` environment – we use DataSphere preprod server.
      - Define path to YandexInternalCA with env variable `ROOT_CA` (see https://wiki.yandex-team.ru/security/ssl/sslclientfix).
      - Use some real project ID, i.e. `b3pbocd5dua07ojecibq`.
  - Now, you can run tests using two different ways:
    - _Debug scenario_ – run client and server (in case of `DEV` environment) manually with `python` to preserve 
      possibility of debugging with your IDE.
      - Run client app, using `SERVER_ENV=ENV python launcher.py`, where `ENV := [DEV | PREPROD]`.
      - Add additional environment variables if needed depends on server environment 
        (S3 secrets for `DEV`, root CA path for `PREPROD`).
    -  _Test scenario_ – run `test_execution.py`, specifying `SERVER_ENV` environment variable. This test scripts will
      run client and server (in case of `DEV` environment) for you. Client will be called as in real use-cases, with
      `datasphere` CLI command. Test script checks expected results – output files, etc. You will still have to 
      provide environment variables and program arguments, needed for client and server to run 
      (see test sources for info).
        - If you create pytest runner configuration in PyCharm for E2E tests, do the following:
          - Add `PYTHONUNBUFFERED=1` to environment variables and `-s` to additional pytest arguments so pytest will not 
          buffer client and server mock std logs.
          - In case of `SERVER_ENV=DEV`, pass server mock arguments with environment variables instead of program 
          arguments.
  - Asserts and E2E tests are linked to launching program – `main.py`, `lib/`.
    - TODOs
      - Create several programs with different use-cases.
      - Test running with re-attach, cancel and other flows.
- Public new version of pip package
  - Follow steps from `Setup`.
  - Run `tox` for tests and other checks on supported Python versions.
  - Run `python -m build && python -m twine upload dist/*`
- TODOs
  - `yandexcloud` package sets up `yandex` root module, and it's not namespace package. At the same time we have
  DataSphere Jobs API protobuf files which is better located in `yandex` with some package hierarchy depending on
  prod/preprod, but we can't locate in `yandex` because of `yandexcloud`. So we locate them in `yandexproto` without
  proper hierarchy.

Useful links:
- https://protobuf.dev/reference/python/python-generated/
- https://grpc.io/docs/languages/python/quickstart/
- https://cloud.yandex.ru/docs/storage/concepts/pre-signed-urls
- https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html