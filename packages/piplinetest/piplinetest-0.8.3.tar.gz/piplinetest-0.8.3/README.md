# Piplinetest

A Python library for building HTTP pipeline tests based on pydantic.

## Project Overview

This project provides base classes for constructing test steps and test classes.

## Installation

You can install the `piplinetest` library using the following command:

```shell
pip install piplinetest
```

## Usage

Import the required classes and functions:

```python
from piplinetest import BaseTestStep, BasePipLineTest
from typing import List

# Create a test step:
class HttpTestStep(BaseTestStep):
    description: str = "test"
    url: str = "/api/request_log"
    method: str = "GET"
    headers: dict = {}
    process_methods_prefix = "tests.process_methods."
    pre_process_method = "pre_process:process_nothing"

# Create a test class instance:
class HttpPipelineTest(BasePipLineTest):
    description: str = "test"
    test_steps_list: List[HttpTestStep] = [
        HttpTestStep,
    ]

# Execute the test class:
t = HttpPipelineTest(host="http://127.0.0.1:5001")
t.execute()
```

## Contributing

Contributions and issues are welcome. You can contribute to the project by following these steps:

1. Fork the project
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Submit a pull request

Feel free to contribute code or raise any questions you may have.
