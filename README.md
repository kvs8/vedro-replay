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
usage: vedro-replay generate [-h] [--path-requests PATH_REQUESTS] [--force] 
                    [{all,vedro_cfg,config,interfaces,contexts,helpers,helpers_methods,scenarios}] - by default all

positional arguments:
  {all,vedro_cfg,interfaces,contexts,helpers,helpers_methods,scenarios}
                        Generation option

options:
  -h, --help            show this help message and exit
  --path-requests PATH_REQUESTS
                        The path to the directory containing the request files
  --force               Forced regeneration. The files will be overwritten
```

To be able to generate a test, you need to have a directory with files containing GET requests 
(`requests` directory is expected by default, you can specify a specific directory using the `--path_requests` argument).
_(So far only use of GET requests is possible)_

Example:
```shell
tests # Root directory
|----requests
|----|----byid.txt # File with API requests of the /byid method
|----|----search.txt # File with API requests of the /search method
```

Example of file contents:
```shell
$ cat requests/byid.txt
/byid?id=123
/byid?id=234
...
```
Having requests, you can generate tests on them:
```shell
$ vedro-replay generate
```
Example of generation:
```
tests # Root directory
|----requests
|----|----byid.txt # File with API requests of the /byid method
|----|----search.txt # File with API requests of the /search method
|----contexts 
|----helpers
|----interfaces 
|----scenarios # Testing scenarios
|----|----byid.py # Scenario, using requests from a file requests/byid.txt
|----|----search.py
|----config.py
|----vedro.cfg.py
```

### Running tests
To run the tests, need two hosts to send requests to them. You need to set environment variables in any convenient way:
```shell
GOLDEN_API_URL=http://master.app
TESTING_API_URL=http://branch.app
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