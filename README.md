# vedro-replay

## Documentation

### replay-tests
The idea is to test the API using requests that are sent to the production application. 
Having requests, we can send them to the API of the test version and to the API of the stable version. 
After receiving two responses from two versions of the application, you can compare the response status, headers, and body. 
The stable version in this case is considered to work correctly and in case of a difference in the answers it means that there is a bug in the test version of the application.

### vedro-replay
Python package for working with replay tests on vedro (docs: [vedro.io](https://vedro.io/docs/quick-start)) framework. 
Enable generation of replay-tests by request files and contains the necessary tools for working and configuring tests.


## Installation
```shell
$ pip3 install vedro-replay
```


## Usage

### Commands
```shell
$ vedro-replay -h
```
```
usage: vedro-replay [-h] {generate} ...

vedro-replay commands

positional arguments:
  {generate}  List of available commands
    generate  Generate vedro-replay tests

options:
  -h, --help  show this help message and exit
```

#### Generate vedro-replay tests
```shell
$ vedro-replay genearate -h
```
```
usage: vedro-replay generate [-h] [--requests-dir REQUESTS_DIR] [--force] 
                    [{all,vedro_cfg,config,interfaces,contexts,helpers,helpers_methods,scenarios}] - by default all

positional arguments:
  {all,vedro_cfg,interfaces,contexts,helpers,helpers_methods,scenarios}
                        Generation option

options:
  -h, --help            show this help message and exit
  --requests-dir REQUESTS_DIR
                        The path to the directory containing the request files
  --force               Forced regeneration. The files will be overwritten
```

To be able to generate a test, you need to have a directory with files containing requests 
(`requests` directory is expected by default, you can specify a specific directory using the `--requests-dir` argument).

Example:
```shell
tests # Root directory
|----requests
|----|----byid.http # File with API requests of the /byid method
|----|----search.http # File with API requests of the /search method
```

Example of file contents (for more information about the request format, see the following paragraph):
```shell
$ cat requests/byid.http
### byid request with id=123
GET http://{{host}}/byid?id=123
```
Having requests, you can generate tests on them:
```shell
$ vedro-replay generate
```
Example of generation:
```
tests # Root directory
|----requests
|----|----byid.http # File with API requests of the /byid method
|----|----search.http # File with API requests of the /search method
|----contexts 
|----helpers
|----interfaces 
|----scenarios # Testing scenarios
|----|----byid.py # Scenario, using requests from a file requests/byid.http
|----|----search.py
|----config.py
|----vedro.cfg.py
```

### Request format
The request format is based on 
[format .http from jetbrains](https://www.jetbrains.com/help/idea/exploring-http-syntax.html)  
The structure of the request has the following form:
```shell
### Comment
Method Request-URI
Header-field: Header-value

JSON-Body
```

Rules:
- Each request starts with a string with the characters "###" at the beginning.
Also on the same line it is possible to write a comment (optional) to the query that will be output in the test being run.
- http method must consist of capital letters
- Request-URI should always have the format http(s)://{{host}}[path][query].
The host looks like this, for the ability to send requests for tests using an http client inside the IDE Idea/Pycharm/...
- Headers are optional
- Json-body is optional

Examples can be found [here](tests/unit/test_data/get_requests.http) and [here](tests/unit/test_data/post_requests.http)

### Running tests
To run the tests, need two hosts to send requests to them. You need to set environment variables in any convenient way:
```shell
GOLDEN_API_URL=master.app
TESTING_API_URL=branch.app
```

After that, you can run the tests:
```shell
$ vedro run -vvv 
```

### Setting up scenario
Sometimes there may be fields or headers in the API response that have a random value or that will differ from the value from the response from the test application. 
Such values will not allow testing, so they must be cut from the comparison of the two answers.

```python
# helpers/helpers.py:

def prepare_byid(response) -> Response: # Generated method for scenario byid.py
   exclude_headers = ['date'] # Date header exclusion
   exclude_body = ['meta.api_version'] # Excluding a field from the body
   return filter_response(JsonResponse(response), exclude_headers, exclude_body)
```