# pytest-spec2md

[![PyPI version](https://badge.fury.io/py/pytest-spec2md.svg)](https://badge.fury.io/py/pytest-spec2md)

This project is an add-on to pytest. It generates a markdown files as specification, while running the tests.

This project is inspired by [pytest-spec](https://github.com/pchomik/pytest-spec) and [pytest-honors](https://github.com/aminohealth/pytest-honors)  .

## Getting started

Install the module using pip.

```
pip install pytest-spec2md
```

Then you can activate the module using *--spec2md* Parameter when calling pytest. 
You should set *--spec2md-version* to embed this value in the final document.

You find the generated markdown files under *docs* folder, if not changed in config.

## Configuration

You can change the target directory using the parameter *spec_target_file*.

```ini
[pytest]
test_spec_target_file = path/to/target/test/spec/file
spec_source_file = path/to/source/spec/file
spec_target_file = path/to/target/spec/with/test/file
```

## Using markers

The plugin provides the marker *func_reference*. This marker can be used to connect a test_case with the testing object.
The name of testing object will than be added to the documentation. If an optional documentation is provided, this will
also be displayed.

The marker can be used at every layer of testing object, so you can also use it at a class.

Furthermore, it provides the marker *spec_identifier*. This identifier can be used, to connect tests with the identifier 
in the specification document.

#### Example

```python
import pytest


def function_to_ref():
    """ Simple doc comment
    with two lines
    """
    pass


@pytest.mark.func_reference(function_to_ref.__name__, function_to_ref.__doc__)
def test_use_a_reference_in_doc():
    assert True

    
@pytest.mark.spec_identifier('Spec.FuntionA')
def test_uses_identifier_from_spec():
    assert True
```

## Examples

Examples for the usage can be found here:
[UseCases on GitHub](https://github.com/mh7d/pytest-spec2md/tree/main/pytester_cases)
