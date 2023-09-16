# Rethink

A note-taking app dependent on python.

## Installation

```shell
pip install rethink
```

## Usage

```python
import rethink

rethink.run()
```

```python
import rethink

rethink.run(
    host='localhost',
    port=8080,
    reload=True,
    workers=1,
)
```
