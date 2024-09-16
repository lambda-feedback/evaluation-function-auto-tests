# Autotests

This library, built for [Lambda Feedback](https://www.lambdafeedback.com/), allows tests defined in a config file to be run on evaluation functions. It is also used by [EvalDocsLoader](https://github.com/lambda-feedback/EvalDocsLoader/)
to auto-generate examples for the documentation.

## Usage

### Test file format
The tests are defined in a YAML file. For the purposes of testing, this file can have any name
and location, but if you want it to be found by EvalDocsLoader, it must be called `eval_tests.yaml`
and located in the repository's root directory. 

The following sample shows the format of the test file, and uses most of the features currently available.

```yaml

---
# Tests should be divided into groups that test related functionality
title: Test Group 1 
tests:
  - description: Tests should have a description that describes what they test
    # Parameters can be given, but this field can be removed if none are needed
    params: {}
    # YAML doesn't require quotes around strings, but they should be used whenever
    # special characters are present, to avoid any issues.
    answer: "x + y" 
    response: "x + y"
    # expected_result is compared against the output of evaluation_function
    # Only is_correct is required, any other fields will be tested only if present
    expected_result:
      is_correct: true
      response_latex: "x + y"

  - description: > 
        This is a second test in the same test group.
        Multi-line strings are possible using YAML's > syntax
    answer: "x + y"
    response: "x - (-y)"
    expected_result:
      is_correct: true
# Tests can be divided into groups using '---'
---
# This illustrates how sub-tests can be used to share the same answer and parameters
# for multiple tests.
title: Test Group 3
tests:
  - description: This test has sub-tests. Sub-tests share the same answer and parameters.
    answer: "x*y"
    sub_tests:
      - description: Sub-test 1
        response: "x*y"
        expected_result:
          is_correct: true
      - description: Sub-test 2
        response: "xy"
        expected_result:
          is_correct: true
      # If a sub-test has no description, it "inherits" the description of the previous test.
      # When EvalDocsLoader generates examples, it combines these sub-tests with the previous
      # test in one table.
      - response: "(x)(y)"
        expected_result:
          is_correct: true
```

A JSON schema for this format is given in `test_schema.json`. This can be used to provide
autocompletion and some basic error detection in your IDE. This has been tested in VSCode 
using the [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) extension.

### Integrating with existing unit tests

Lambda Feedback evaluation functions use Python's unit testing framework,
where the tests are methods of a class that inherits from `unittest.TestCase`.

This library provides a decorator that adds the necessary code to this class to 
load the test file and run all the tests contained in it:

```python

import unittest
from autotests import auto_test
from .evaluation import evaluation_function


@auto_test("eval_tests.yaml", evaluation_function)
class TestEvaluationFunction(unittest.TestCase):

    def test_existing_test_case(self):
        # Any existing test cases that aren't in YAML form are unaffected
        pass

```

The first argument to the decorator is the path to the test file, relative to the repository
root. The second argument is the evaluation function to test. This will add an extra test
to the class, called `test_auto`, that will run all the tests contained in the file.
