# pandas-validity

## What is it?
**pandas-validity** is a Python library for validation of pandas DataFrames. It provides a `DataFrameValidator` class that serves as a context manager. Within this context, you can perform multiple validations and checks. Any encountered errors are collected and raised at the end of the process. The `DataFrameValidator` raises a `ValidationErrorsGroup` exception to summarize the errors.

## Where to get it?
You can easily install the latest released version using binary installers from the [Python Package Index (PyPI)](https://pypi.org/project/pandas-validity):

```sh
pip install pandas-validity
```

## Usage
```python
import pandas as pd
import datetime
from pandas_validity.validator import DataFrameValidator

# Create a sample DataFrame
df = pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": ["a", None, "c"],
            "C": [2.3, 4.5, 9.2],
            "D": [
                datetime.datetime(2023, 1, 1, 1),
                datetime.datetime(2023, 1, 1, 2),
                datetime.datetime(2023, 1, 1, 3),
            ],
        }
    )

# Define your expectations and data type mappings
expected_columns = ['A', 'B', 'C', 'E']
data_types_mapping = {
            "A": 'float',
            "D": 'datetime'
        }

# Use DataFrameValidator for validation
with DataFrameValidator(df) as validator:
    validator.is_empty()
    validator.has_required_columns(expected_columns)
    validator.has_no_redundant_columns(expected_columns)
    validator.has_valid_data_types(data_types_mapping)
    validator.has_no_missing_data()
```

**Output:**
```shell
Error occurred: (<class 'pandas_validity.exceptions.ValidationError'>) The dataframe has missing columns: ['E']
Error occurred: (<class 'pandas_validity.exceptions.ValidationError'>) The dataframe has redundant columns: ['D']
Error occurred: (<class 'pandas_validity.exceptions.ValidationError'>) Column 'A' has an invalid data type: 'int64'
Error occurred: (<class 'pandas_validity.exceptions.ValidationError'>) Found 1 missing value: [{'index': 1, 'column': 'B', 'value': None}]
  + Exception Group Traceback (most recent call last):
...
  | pandas_validity.exceptions.ValidationErrorsGroup: Validation errors found: 4. (4 sub-exceptions)
  +-+---------------- 1 ----------------
    | pandas_validity.exceptions.ValidationError: The dataframe has missing columns: ['E']
    +---------------- 2 ----------------
    | pandas_validity.exceptions.ValidationError: The dataframe has redundant columns: ['D']
    +---------------- 3 ----------------
    | pandas_validity.exceptions.ValidationError: Column 'A' has an invalid data type: 'int64'
    +---------------- 4 ----------------
    | pandas_validity.exceptions.ValidationError: Found 1 missing value: [{'index': 1, 'column': 'B', 'value': None}]
    +------------------------------------
```

## Development
**Prerequisites**: [poetry](https://python-poetry.org/) for environment management 

The source code is currently hosted on GitHub at:
[https://github.com/ohmycoffe/pandas-validity](https://github.com/ohmycoffe/pandas-validity)

```shell
git clone git@github.com:ohmycoffe/pandas-validity.git
```
To install project and development dependencies:
```shell
make install 
```
To run tests:
```shell
make test 
```
To view all possible commands, use:
```shell
make 
```
## License
This project is licensed under the terms of the [MIT](LICENSE) license.
