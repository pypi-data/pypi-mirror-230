# python-io-capture

capture and report function IO at runtime

## Installation

```bash
pip3 install python-io-capture
```

## Usage

```python
from example import example
from py_io_capture import decorate_module, dump_records
import atexit

example = decorate_module(example)
atexit.register(dump_records, "demo_dump.json")

if __name__ == "__main__":
    example.main()
```
