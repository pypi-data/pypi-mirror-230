| | |
| --- | --- |
| Python| ![Python](https://img.shields.io/pypi/pyversions/pycsi) |
| Package | [![PyPI Latest Release](https://img.shields.io/pypi/v/pycsi.svg)](https://pypi.org/project/pycsi/) [![PyPI Downloads](https://img.shields.io/pypi/dm/pycsi.svg?label=PyPI%20downloads)](https://pypi.org/project/pycsi/) [![codecov](https://codecov.io/gh/EM51641/csi/graph/badge.svg?token=K1VoKFacbb)](https://codecov.io/gh/EM51641/csi)|
| Meta | [![License - MIT](https://img.shields.io/pypi/l/pycsi.svg)](https://github.com/EM51641/csi/blob/main/LICENSE)|


# pycsi

pycsi is a simple python library to validate data and/or build a validation schema.

# Installation

```bash
pip install pycsi
```

# Usage
We might begin by creating validation callables such:
    
```python
def is_divisible_by_three(x: float):
    return x % 3 == 0

def is_all_positive(numbers: list[float]):
    return all(number > 0 for number in numbers)

def is_quotient_positive(x: float, y: float):
    return x / y > 0

```

Then we can instantiate a ```Subvalidator``` instance and  the validation callables to it:

```python
from pycsi import Subvalidator

first_subvalidator = Subvalidator(
    "First condition",
    "Number is not divisible by 3",
    is_divisible_by_three,
    x=3
    )

second_subvalidator = Subvalidator(
    "Second condition",
    "Not every number is positive",
    is_all_positive,
    numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, -10],
    )

third_subvalidator = Subvalidator(
    "Third condition",
    "Quotient is not positive",
    is_quotient_positive,
    x=10,
    y=2,
    )
```

Finally we can create a validator object and add the subvalidators to it.

```python
from pycsi import Validator

validator = Validator()

validator.add(first_subvalidator)
validator.add(second_subvalidator)
validator.add(third_subvalidator)

validator.run()
```

The validator will run all the subvalidators and the `unvalidated_set` property will return a set of the failed subvalidators.
```python
print(validator.unvalidated_set)
{ValidatorError(condition='Second condition', error_message='Not every number is positive')}
```

# Asynchronous Usage

This library also supports async validation. We can create asyncronous validation callables such:

```python
import asyncio

async def async_is_divisible_by_three(x: float) -> bool:
    await asyncio.sleep(0.1)
    return is_divisible_by_three(x)

async def async_is_all_positive(numbers: list[float]) -> bool:
    await asyncio.sleep(0.1)
    return is_all_positive(numbers)
```

Instead of using the ```Subvalidator``` API, we are going to use the ```AsyncSubvalidator``` in the next step:

```python
from pycsi import AsyncSubvalidator

first_subvalidator = AsyncSubvalidator(
    "First condition",
    "Number is not divisible by 3",
    async_is_divisible_by_three,
    x=10,
    )

second_subvalidator = AsyncSubvalidator(
    "Second condition",
    "Not every number is positive",
    async_is_all_positive,
    numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    )
```

Same for the ```Validator``` API, we will switch the the ```AsyncValidator```.

```python
from pycsi import AsyncValidator

validator = AsyncValidator()
validator.add(first_subvalidator)
validator.add(second_subvalidator)

validator.run()
print(validator.unvalidated_set)
{ValidatorError(condition='First condition', error_message='Number is not divisible by 3')}
```
