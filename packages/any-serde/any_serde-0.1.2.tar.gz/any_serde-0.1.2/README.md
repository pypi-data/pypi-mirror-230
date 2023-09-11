# AnySerde

AnySerde is a Python package that simplifies the task of converting Python variables to and from serializable data. Whether you need to serialize Python objects to JSON, YAML, or other common formats, or deserialize data from these formats back into Python objects, AnySerde has got you covered.

The main difference from other serialization libraries is that AnySerde does not require any changes to your existing codebase such as adding decorators or adding parent classes.

## Installation

You can easily install AnySerde using pip:

```bash
pip install any_serde
```

More package details on the [PyPI page](https://pypi.org/project/any-serde):

## Usage

Using AnySerde is straightforward. Here's a quick overview of how to get started:

### Converting Python Objects to Data

To convert a Python variable to a data format (e.g., JSON or YAML), you can use the `to_data` function. Here's an example with a dataclass:

```python
from dataclasses import dataclass
import yaml
from any_serde import to_data

@dataclass
class SampleDataclass:
    foo: int
    bar: str
    baz: dict[str, list[bool]]

sample = SampleDataclass(
    foo=2,
    bar="some text",
    baz={"0": [], "8": [True, False, False]},
)
sample_data = to_data(SampleDataclass, sample)

with open("sample.yaml", "wt") as f:
    yaml.dump(sample_data, f)
```

This example dumps the data as yaml to a file, but you could easily use json or xml or any other format you want.

### Converting Data to Python Objects

Conversely, if you have data in a specific format and want to convert it back to a Python object, you can use the `from_data` function. Here's a continuation of the previous example that turns the yaml file back into a python variable:

```python
from any_serde import from_data

with open("sample.yaml", "rt") as f:
    sample_data = yaml.load(f, Loader=yaml.SafeLoader)

sample = from_data(SampleDataclass, sample_data)
```

Again, you can replace `'json'` with the desired format.

## Supported Object Types

Right now, AnySerde can convert these types to data:

1. All python primitives except `complex`
1. dictionaries
1. lists
1. sets
1. tuples
1. union types (but be careful of ambiguous serialization)
1. Dataclasses
1. Enums

As of writing this, AnySerde plans to support these types (but doesn't yet):

1. NamedTuple
1. Path
1. Datetime
1. all other builtin python types
1. user-defined types (with user-defined to_data and from_data methods)

## Contributing

Contributions to AnySerde are welcome! If you find a bug, have a feature request, or want to contribute code, please open an issue or submit a pull request on the [GitHub repository](https://github.com/derekmod/any_serde).

## License

AnySerde is available for any use (including commercial) and is distributed under the Apache License 2.0. See the [LICENSE](https://github.com/Derekmod/any_serde/blob/master/LICENSE) file for more details.
